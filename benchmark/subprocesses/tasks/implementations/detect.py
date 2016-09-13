import logging
import time
from enum import Enum, IntEnum
from os import makedirs
from os.path import join, realpath, exists
from typing import Dict
from typing import Optional, List
from urllib.error import URLError

import yaml

from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.requirements import JavaRequirement
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark.utils.io import remove_tree, write_yaml, read_yaml
from benchmark.utils.shell import Shell, CommandFailedError
from benchmark.utils.web_util import download_file


class Result(Enum):
    error = 0
    success = 1
    timeout = 2


class Run:
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    def __init__(self, path: str):
        self.__path = path
        self.__findings_file_path = join(path, Run.FINDINGS_FILE)
        self.__run_file_path = join(path, Run.RUN_FILE)
        self.result = None  # type: Result
        self.runtime = None  # type: float
        self.detector_md5 = None  # type: Optional[str]
        self.message = ""
        self.__findings = []  # type: List[Dict[str,str]]
        if exists(self.__run_file_path):
            data = read_yaml(self.__run_file_path)
            self.result = Result[data["result"]]
            self.runtime = data.get("runtime", -1)
            self.detector_md5 = data.get("md5", None)
            self.message = data.get("message", "")

    def is_success(self):
        return self.result == Result.success

    def is_failure(self):
        return self.result == Result.error or self.result == Result.timeout

    @property
    def findings(self):
        if not self.__findings:
            if exists(self.__findings_file_path):
                with open(self.__findings_file_path, "r") as stream:
                    self.__findings = [finding for finding in yaml.load_all(stream) if finding]
        return self.__findings

    def write(self, detector_md5: str):
        run_data = read_yaml(self.__run_file_path) if exists(self.__run_file_path) else {}
        run_data.update(
            {"result": self.result.name, "runtime": self.runtime, "message": self.message, "md5": detector_md5})
        write_yaml(run_data, file=self.__run_file_path)

    def reset(self):
        path = self.__path
        remove_tree(path)
        self.__init__(path)


class DetectorMode(IntEnum):
    mine_and_detect = 0
    detect_only = 1


class Detect(ProjectVersionTask):
    def __init__(self, detector: str, detector_result_file: str, compiles_base_path: str, results_base_path: str,
                 experiment: int, timeout: Optional[int], java_options: List[str], force_detect: bool):
        super().__init__()
        self.force_detect = force_detect  # type: bool
        self.detector = detector  # type: str
        self.detector_findings_file = detector_result_file  # type: str
        self.compiles_base_path = compiles_base_path  # type: str
        self.results_base_path = results_base_path  # type: str
        self.detector_mode = Detect._get_detector_mode(experiment)  # type: DetectorMode
        self.timeout = timeout  # type: Optional[int]
        self.java_options = ['-' + option for option in java_options]  # type: List[str]

        self.key_findings_file = "target"
        self.key_detector_mode = "detector_mode"
        self.key_training_src_path = "training_src_path"
        self.key_training_classpath = "training_classpath"
        self.key_target_src_path = "target_src_path"
        self.key_target_classpath = "target_classpath"

    def get_requirements(self):
        return [JavaRequirement()]

    def start(self):
        logger = logging.getLogger("detect")
        msg = "Running '{}' detector".format(self.detector)
        if self.force_detect:
            msg += " with forced detection and"
        if self.timeout:
            msg += " with a timeout of {}s".format(self.timeout)
        else:
            msg += " without timeout."
        logger.info(msg)

        if not self._detector_available():
            self._download()

    def _detector_available(self) -> bool:
        return exists(Detect.__get_misuse_detector_path(self.detector))

    def _download(self):
        logger = logging.getLogger("detect")
        url = Detect.__get_misuse_detector_url(self.detector)
        logger.info("Loading detector from '%s'...", url)
        file = Detect.__get_misuse_detector_path(self.detector)
        md5_file = Detect.__get_misuse_detector_md5_file(self.detector)

        try:
            if not exists(md5_file):
                raise FileNotFoundError("Cannot validate download, MD5-checksum file '{}' missing".format(md5_file))

            download_file(url, file, md5_file)
        except (FileNotFoundError, ValueError, URLError) as e:
            logger.error("Download failed: %s", e)
            exit(1)

    def process_project_version(self, project: Project, version: ProjectVersion) -> Response:
        logger = logging.getLogger("detect")

        result_path = join(self.results_base_path, version.project_id, version.version_id)
        run = Run(result_path)

        if run.result == Result.error and not self._new_detector_available(run):
            logger.info("Error in previous run for %s. Skipping detection.", version)
            return Response.skip
        elif self.detector_mode == DetectorMode.detect_only and not version.patterns:
            logger.info("No patterns for %s. Skipping detection.", version)
            return Response.skip
        elif run.is_success() and not self.force_detect and not self._new_detector_available(run):
            logger.info("Detector findings for %s already exists. Skipping detection.", version)
            return Response.ok
        else:
            run.reset()

            findings_file_path = join(result_path, self.detector_findings_file)
            detector_path = Detect.__get_misuse_detector_path(self.detector)
            detector_args = self.get_detector_arguments(findings_file_path, version)

            remove_tree(result_path)
            makedirs(result_path, exist_ok=True)
            logger.info("Detecting misuses in %s...", version)
            logger.debug("- Detector path = %s", detector_path)
            logger.debug("- Detector args = %s", detector_args)
            logger = logging.getLogger("detect.run")
            start = time.time()
            try:
                self._invoke_detector(detector_path, detector_args)
                run.result = Result.success
            except CommandFailedError as e:
                logger.error("Detector failed: %s", e)
                run.result = Result.error
                run.message = str(e)
            except TimeoutError:
                logger.error("Detector took longer than the maximum of %s seconds", self.timeout)
                run.result = Result.timeout
            finally:
                end = time.time()
                runtime = end - start
                run.runtime = runtime

        run.write(Detect.__get_misuse_detector_md5(self.detector))

        if run.is_success():
            logger.info("Detection took {0:.2f} seconds.".format(runtime))
            return Response.ok
        else:
            return Response.skip

    def get_detector_arguments(self, findings_file_path: str, version: ProjectVersion) -> List[str]:
        project_compile = version.get_compile(self.compiles_base_path)
        findings_file = [self.key_findings_file, self.to_arg_path(findings_file_path)]
        detector_mode = [self.key_detector_mode, self.to_arg_path(str(int(self.detector_mode)))]

        training_src_path = []
        training_classpath = []
        target_src_path = []
        target_classpath = []
        if self.detector_mode == DetectorMode.detect_only:
            training_src_path = [self.key_training_src_path, self.to_arg_path(project_compile.pattern_sources_path)]
            training_classpath = [self.key_training_classpath, self.to_arg_path(project_compile.pattern_classes_path)]
            target_src_path = [self.key_target_src_path, self.to_arg_path(project_compile.misuse_source_path)]
            target_classpath = [self.key_target_classpath, self.to_arg_path(project_compile.misuse_classes_path)]
        elif self.detector_mode == DetectorMode.mine_and_detect:
            target_src_path = [self.key_target_src_path, self.to_arg_path(project_compile.original_sources_path)]
            target_classpath = [self.key_target_classpath, self.to_arg_path(project_compile.original_classes_path)]

        return findings_file + detector_mode + training_src_path + training_classpath + target_src_path + target_classpath

    def _invoke_detector(self, absolute_misuse_detector_path: str, detector_args: List[str]):
        command = ["java"] + self.java_options + ["-jar",
                                                  self.to_arg_path(absolute_misuse_detector_path)] + detector_args
        command = " ".join(command)
        return Shell.exec(command, logger=logging.getLogger("detect.run"), timeout=self.timeout)

    def _new_detector_available(self, run: Run) -> bool:
        return not Detect.__get_misuse_detector_md5(self.detector) == run.detector_md5

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
    def __get_misuse_detector_md5_file(detector: str):
        return join(Detect.__get_misuse_detector_dir(detector), detector + ".md5")

    @staticmethod
    def __get_misuse_detector_md5(detector: str) -> Optional[str]:
        md5_file = Detect.__get_misuse_detector_md5_file(detector)
        md5 = None

        if exists(md5_file):
            with open(md5_file) as file:
                md5 = file.read()

        return md5

    @staticmethod
    def _get_detector_mode(experiment: int) -> DetectorMode:
        if experiment == 1:
            return DetectorMode.detect_only
        elif experiment == 2:
            return DetectorMode.mine_and_detect
        elif experiment == 3:
            return DetectorMode.mine_and_detect
        else:
            raise ValueError("Invalid experiment {}".format(experiment))
