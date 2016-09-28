import logging
import time
from os.path import exists
from typing import Optional, List
from urllib.error import URLError

from benchmark.data.experiment import Experiment, DetectorMode
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.data.run import Run, Result
from benchmark.subprocesses.requirements import JavaRequirement
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark.utils.shell import Shell, CommandFailedError
from benchmark.utils.web_util import download_file


class Detect(ProjectVersionTask):
    def __init__(self, compiles_base_path: str, experiment: Experiment, timeout: Optional[int], java_options: List[str],
                 force_detect: bool):
        super().__init__()
        self.force_detect = force_detect
        self.compiles_base_path = compiles_base_path
        self.experiment = experiment
        self.detector = experiment.detector
        self.timeout = timeout
        self.java_options = ['-' + option for option in java_options]

        self.key_findings_file = "target"
        self.key_run_file = "run_info"
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
        return exists(self.detector.jar_path)

    def _download(self):
        logger = logging.getLogger("detect")
        url = self.detector.jar_url
        logger.info("Loading detector from '%s'...", url)
        file = self.detector.jar_path

        try:
            if not exists(self.detector.md5_path):
                raise FileNotFoundError("Cannot validate download, MD5-checksum file '{}' missing".format(self.detector.md5_path))
            download_file(url, file, self.detector.md5_path)
        except (FileNotFoundError, ValueError, URLError) as e:
            logger.error("Download failed: %s", e)
            exit(1)

    def process_project_version(self, project: Project, version: ProjectVersion) -> Response:
        logger = logging.getLogger("detect")
        run = self.experiment.get_run(version)

        if self._detector_updated(run) or self.force_detect:
            pass
        elif run.is_error():
            logger.info("Error in previous %s. Skipping.", run)
            return Response.skip
        elif run.is_success():
            logger.info("Successful previous %s. Skipping.", run)
            return Response.skip
        elif self.experiment.id == Experiment.PROVIDED_PATTERNS and not version.patterns:
            logger.info("No patterns to run with. Skipping.")
            return Response.skip

        run.reset()

        logger.info("Executing %s...", run)
        logger = logging.getLogger("detect.run")
        start = time.time()
        try:
            detector_path = self.detector.jar_path
            detector_args = self.get_detector_arguments(run.findings_file_path, run.run_file_path, run.version)
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
            logger.info("Run took {0:.2f} seconds.".format(runtime))

        run.save(self.detector.md5)

        return Response.ok if run.is_success() else Response.skip

    def get_detector_arguments(self, findings_file_path: str, run_file_path: str, version: ProjectVersion) -> List[str]:
        project_compile = version.get_compile(self.compiles_base_path)
        findings_file = [self.key_findings_file, self.to_arg_path(findings_file_path)]
        run_file = [self.key_run_file, self.to_arg_path(run_file_path)]
        detector_mode = [self.key_detector_mode, self.to_arg_path(str(int(self.experiment.detector_mode)))]

        training_src_path = []
        training_classpath = []
        target_src_path = []
        target_classpath = []
        if self.experiment.detector_mode == DetectorMode.detect_only:
            training_src_path = [self.key_training_src_path, self.to_arg_path(project_compile.pattern_sources_base_path)]
            training_classpath = [self.key_training_classpath, self.to_arg_path(project_compile.pattern_classes_base_path)]
            target_src_path = [self.key_target_src_path, self.to_arg_path(project_compile.misuse_source_path)]
            target_classpath = [self.key_target_classpath, self.to_arg_path(project_compile.misuse_classes_path)]
        elif self.experiment.detector_mode == DetectorMode.mine_and_detect:
            target_src_path = [self.key_target_src_path, self.to_arg_path(project_compile.original_sources_path)]
            target_classpath = [self.key_target_classpath, self.to_arg_path(project_compile.original_classes_path)]

        return findings_file + run_file + detector_mode + training_src_path + training_classpath + target_src_path + \
               target_classpath

    def _invoke_detector(self, absolute_misuse_detector_path: str, detector_args: List[str]):
        command = ["java"] + self.java_options + ["-jar",
                                                  self.to_arg_path(absolute_misuse_detector_path)] + detector_args
        command = " ".join(command)
        return Shell.exec(command, logger=logging.getLogger("detect.run"), timeout=self.timeout)

    def _detector_updated(self, run: Run) -> bool:
        return not self.detector.md5 == run.detector_md5

    @staticmethod
    def to_arg_path(absolute_misuse_detector_path):
        return "\"{}\"".format(absolute_misuse_detector_path)
