import logging
import subprocess
import time
from enum import Enum
from os import makedirs
from os.path import join, realpath, exists
from typing import Optional, List

import yaml

from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark.utils import web_util
from benchmark.utils.io import remove_tree
from benchmark.utils.shell import Shell, CommandFailedError


class Result(Enum):
    error = 0
    success = 1
    timeout = 2


class Detect(ProjectVersionTask):
    def __init__(self, detector: str, detector_result_file: str, compiles_base_path: str, results_base_path: str,
                 timeout: Optional[int], java_options: List[str], force_detect: bool):
        super().__init__()
        self.force_detect = force_detect
        self.detector = detector
        self.detector_findings_file = detector_result_file
        self.compiles_base_path = compiles_base_path
        self.results_base_path = results_base_path
        self.timeout = timeout
        self.java_options = ['-' + option for option in java_options]

        self.key_findings_file = "target"
        self.key_src_project = "src"
        self.key_src_patterns = "src_patterns"
        self.key_classes_project = "classpath"
        self.key_classes_patterns = "classpath_patterns"

    def enter(self):
        if not self._detector_available():
            self._download()

    def _detector_available(self) -> bool:
        return exists(Detect.__get_misuse_detector_path(self.detector))

    def _download(self) -> bool:
        return web_util.load_detector(Detect.__get_misuse_detector_url(self.detector),
                                      Detect.__get_misuse_detector_path(self.detector),
                                      Detect.__get_misuse_detector_md5(self.detector))

    def process_project_version(self, project: Project, version: ProjectVersion) -> Response:
        logger = logging.getLogger("detect")

        result_path = join(self.results_base_path, version.project_id, version.version_id)
        findings_file_path = join(result_path, self.detector_findings_file)
        result_file_path = join(result_path, "result.yml")

        detector_path = Detect.__get_misuse_detector_path(self.detector)
        detector_args = self.get_detector_arguments(findings_file_path, project, version)
        print(result_file_path)

        if exists(result_file_path) and not self.force_detect:
            logger.info("Detector findings for %s already exists. Skipping detection.", version)
            return Response.ok
        else:
            remove_tree(result_path)
            makedirs(result_path, exist_ok=True)
            logger.info("Detecting misuses in %s...", version)
            logger.debug("- Detector path = %s", detector_path)
            logger.debug("- Detector args = %s", detector_args)
            logger = logging.getLogger("detect.run")
            start = time.time()
            try:
                self._invoke_detector(detector_path, detector_args)
                detector_result = Result.success
            except CommandFailedError as e:
                logger.error("Detector failed: %s", e)
                detector_result = Result.error
            except subprocess.TimeoutExpired:
                logger.error("Detector took longer than the maximum of %s seconds", self.timeout)
                detector_result = Result.timeout
            finally:
                end = time.time()
                runtime = end - start

        detector_stats = {"result": detector_result.name, "runtime": runtime}
        with open(result_file_path, "w") as result_file:
            yaml.safe_dump(detector_stats, result_file, default_flow_style=False)

        if detector_result == Result.success:
            logger.info("Detection took {0:.2f} seconds.".format(runtime))
            return Response.ok
        else:
            return Response.skip

    def get_detector_arguments(self, findings_file_path: str, project: Project, version: ProjectVersion) -> List[str]:
        project_compile = version.get_compile(self.compiles_base_path)
        findings_file = [self.key_findings_file, self.to_arg_path(findings_file_path)]
        src_project = [self.key_src_project, self.to_arg_path(project_compile.original_sources_path)]
        src_patterns = []
        classes_project = []
        classes_patterns = []
        if version.patterns:
            src_patterns = [self.key_src_patterns, self.to_arg_path(project_compile.pattern_sources_path)]
        if version.compile_commands:
            classes_project = [self.key_classes_project, self.to_arg_path(project_compile.original_classes_path)]
            if version.patterns:
                classes_patterns = [self.key_classes_patterns, self.to_arg_path(project_compile.pattern_classes_path)]
        return findings_file + src_project + src_patterns + classes_project + classes_patterns

    def _invoke_detector(self, absolute_misuse_detector_path: str, detector_args: List[str]):
        command = ["java"] + self.java_options + ["-jar",
                                                  self.to_arg_path(absolute_misuse_detector_path)] + detector_args
        command = " ".join(command)
        return Shell.exec(command, logger=logging.getLogger("detect.run"), timeout=self.timeout)

    @staticmethod
    def to_arg_path(absolute_misuse_detector_path):
        return "\"{}\"".format(absolute_misuse_detector_path)

    @staticmethod
    def __get_misuse_detector_dir(detector: str):
        return realpath(join("detectors", detector))

    @staticmethod
    def __get_misuse_detector_path(detector: str):
        return join(Detect.__get_misuse_detector_dir(detector), detector + ".jar")

    @staticmethod
    def __get_misuse_detector_url(detector: str):
        return "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/{}.jar".format(detector)

    @staticmethod
    def __get_misuse_detector_md5(detector: str):
        return join(Detect.__get_misuse_detector_dir(detector), detector + ".md5")
