import logging
from os.path import join, exists
from typing import Optional, List
from urllib.error import URLError

from data.detector import Detector
from data.detector_execution import DetectorExecution
from data.findings_filters import PotentialHits
from data.misuse import Misuse
from data.misuse_compile import MisuseCompile
from data.project_version import ProjectVersion
from data.version_compile import VersionCompile
from tasks.configurations.detector_interface_configuration import key_findings_file, key_run_file, key_detector_mode, \
    key_training_src_path, key_training_classpath, key_target_src_path, key_target_classpath, key_dependency_classpath
from utils.web_util import download_file

RUN_MODE_NAME = "detect_only"
DETECTOR_MODE = 1


class DetectProvidingPatternsTask:
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    def __init__(self, detector: Detector, findings_base_path: str, force_detect: bool, timeout: Optional[int]):
        self.detector = detector
        self.findings_base_path = findings_base_path
        self.detector = detector
        self._findings_base_path = findings_base_path

        self.force_detect = force_detect
        self.timeout = timeout

        self.logger = logging.getLogger("task.detect")

        msg = "Running '{}' detector".format(self.detector)
        if self.force_detect:
            msg += " with forced detection and"
        if self.timeout:
            msg += " with a timeout of {}s".format(self.timeout)
        else:
            msg += " without timeout."
        self.logger.info(msg)

        if not self._detector_available():
            self._download()

    def _detector_available(self) -> bool:
        return exists(self.detector.jar_path)

    def _download(self):
        url = self.detector.jar_url
        self.logger.info("Loading detector from '%s'...", url)
        file = self.detector.jar_path

        try:
            md5 = self.detector.md5
            if md5 == Detector.NO_MD5:
                raise ValueError("Missing MD5 for {}".format(self.detector.id))
            download_file(url, file, md5)
        except (FileNotFoundError, ValueError, URLError) as e:
            self.logger.error("Download failed: %s", e)
            exit(1)

    def run(self, version: ProjectVersion, misuse: Misuse, version_compile: VersionCompile,
            misuse_compile: MisuseCompile) -> List[DetectorExecution]:
        detector_execution = self.get_run(version, misuse)

        if detector_execution.is_outdated() or self.force_detect:
            pass
        elif detector_execution.is_error():
            raise UserWarning("Error in previous {}. Skipping.".format(str(detector_execution)))
        elif detector_execution.is_success():
            self.logger.info("Successful previous %s. Skipping.", detector_execution)
            return detector_execution

        detector_execution.reset()

        self.logger.info("Executing %s...", detector_execution)
        logger = logging.getLogger("detect.run")
        detector_execution.execute(self._get_detector_arguments(self._get_findings_path(version, misuse),
                                                                self._get_run_file_path(version, misuse),
                                                                version_compile,
                                                                misuse_compile),
                                   self.timeout, logger)

        if not detector_execution.is_success():
            raise UserWarning("Run {} failed.".format(str(detector_execution)))

        return detector_execution

    def _get_findings_file(self, version, misuse):
        return join(self._get_findings_path(version, misuse), self.FINDINGS_FILE)

    def _get_findings_path(self, version: ProjectVersion, misuse: Misuse):
        return join(self.findings_base_path, RUN_MODE_NAME, self.detector.id,
                    version.project_id, version.version_id, misuse.misuse_id)

    def get_run(self, version: ProjectVersion, misuse: Misuse):
        findings_filter = PotentialHits([misuse])
        return DetectorExecution(self.detector, version, self._get_findings_path(version, misuse), findings_filter,
                                 self._get_findings_file(version, misuse), self._get_run_file_path(version, misuse))

    def _get_run_file_path(self, version, misuse):
        return join(self._get_findings_path(version, misuse), self.RUN_FILE)

    @staticmethod
    def _get_detector_arguments(findings_file_path: str, run_file_path: str, version_compile: VersionCompile,
                                misuse_compile: MisuseCompile):
        return {
            key_findings_file: findings_file_path,
            key_run_file: run_file_path,
            key_detector_mode: DETECTOR_MODE,
            key_training_src_path: misuse_compile.pattern_sources_path,
            key_training_classpath: misuse_compile.pattern_classes_path,
            key_target_src_path: misuse_compile.misuse_source_path,
            key_target_classpath: misuse_compile.misuse_classes_path,
            key_dependency_classpath: version_compile.get_full_classpath()
        }
