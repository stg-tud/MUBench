import logging
from os.path import join
from typing import Optional

from data.detector import Detector
from data.detector_run import DetectorRun
from data.misuse import Misuse
from data.misuse_compile import MisuseCompile
from data.project_version import ProjectVersion
from data.version_compile import VersionCompile
from tasks.configurations.detector_interface_configuration import key_findings_file, key_run_file, key_detector_mode, \
    key_training_src_path, key_training_classpath, key_target_src_path, key_target_classpath, key_dependency_classpath

RUN_MODE_NAME = "detect_only"
DETECTOR_MODE = 1


class DetectProvidedPatternsTask:
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    def __init__(self, findings_base_path: str, force_detect: bool, timeout: Optional[int]):
        self.findings_base_path = findings_base_path
        self.force_detect = force_detect
        self.timeout = timeout

        self.logger = logging.getLogger("task.detect")

    def run(self, detector: Detector, version: ProjectVersion, version_compile: VersionCompile, misuse: Misuse,
            misuse_compile: MisuseCompile):
        run = self._get_run(detector, version, misuse)

        if run.is_outdated() or self.force_detect:
            pass
        elif run.is_failure():
            self.logger.info("Error in previous {}. Skipping.".format(str(run)))
            self.logger.debug("Full exception:", exc_info=True)
            return run
        elif run.is_success():
            self.logger.info("Successful previous %s. Skipping.", run)
            return run

        run.reset()

        self.logger.info("Executing %s...", run)
        logger = logging.getLogger("detect.run")
        run.execute(self._get_detector_arguments(self._get_findings_file_path(detector, version, misuse),
                                                 self._get_run_file_path(detector, version, misuse),
                                                 version_compile, misuse_compile),
                    self.timeout, logger)

        if not run.is_success():
            self.logger.info("Run {} failed.".format(str(run)))
            self.logger.debug("Full exception:", exc_info=True)

        return run

    def _get_run(self, detector: Detector, version: ProjectVersion, misuse: Misuse):
        return DetectorRun(detector, version,
                           self._get_findings_path(detector, version, misuse),
                           self._get_findings_file_path(detector, version, misuse),
                           self._get_run_file_path(detector, version, misuse))

    def _get_run_file_path(self, detector: Detector, version: ProjectVersion, misuse: Misuse):
        return join(self._get_findings_path(detector, version, misuse), self.RUN_FILE)

    def _get_findings_path(self, detector: Detector, version: ProjectVersion, misuse: Misuse):
        return join(self.findings_base_path, RUN_MODE_NAME, detector.id,
                    version.project_id, version.version_id, misuse.misuse_id)

    def _get_findings_file_path(self, detector: Detector, version: ProjectVersion, misuse: Misuse):
        return join(self._get_findings_path(detector, version, misuse), self.FINDINGS_FILE)

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
