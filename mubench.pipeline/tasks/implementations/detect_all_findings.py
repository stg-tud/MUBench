import logging
from os.path import join
from typing import Optional

from data.detector import Detector
from data.detector_run import DetectorRun
from data.project_version import ProjectVersion
from data.version_compile import VersionCompile
from tasks.configurations.detector_interface_configuration import key_findings_file, key_run_file, key_detector_mode, \
    key_target_src_path, key_target_classpath, key_dependency_classpath

RUN_MODE_NAME = "mine_and_detect"
DETECTOR_MODE = 0


class DetectAllFindingsTask:
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    def __init__(self, findings_base_path: str, force_detect: bool, timeout: Optional[int], limit: Optional[int]):
        self.findings_base_path = findings_base_path
        self.force_detect = force_detect
        self.timeout = timeout
        self.limit = limit

        self.logger = logging.getLogger("task.detect")

    def run(self, detector: Detector, version: ProjectVersion, version_compile: VersionCompile):
        run = self._get_run(detector, version)

        if run.is_outdated() or self.force_detect:
            pass
        elif run.is_error():
            raise UserWarning("Error in previous {}. Skipping.".format(str(run)))
        elif run.is_success():
            self.logger.info("Successful previous %s. Skipping.", run)
            return run

        run.reset()

        self.logger.info("Executing %s...", run)
        logger = logging.getLogger("detect.run")
        run.execute(self._get_detector_arguments(self._get_findings_file_path(detector, version),
                                                 self._get_run_file_path(detector, version),
                                                 version_compile),
                    self.timeout, logger)

        if not run.is_success():
            raise UserWarning("Run {} failed.".format(str(run)))

        return run

    def _get_run(self, detector: Detector, version: ProjectVersion):
        return DetectorRun(detector, version,
                           self._get_findings_path(detector, version),
                           self._get_findings_file_path(detector, version),
                           self._get_run_file_path(detector, version))

    def _get_run_file_path(self, detector: Detector, version: ProjectVersion):
        return join(self._get_findings_path(detector, version), self.RUN_FILE)

    def _get_findings_path(self, detector: Detector, version: ProjectVersion):
        return join(self.findings_base_path, RUN_MODE_NAME, detector.id,
                    version.project_id, version.version_id)

    def _get_findings_file_path(self, detector: Detector, version: ProjectVersion):
        return join(self._get_findings_path(detector, version), self.FINDINGS_FILE)

    @staticmethod
    def _get_detector_arguments(findings_file_path: str, run_file_path: str, version_compile: VersionCompile):
        return {
            key_findings_file: findings_file_path,
            key_run_file: run_file_path,
            key_detector_mode: DETECTOR_MODE,
            key_target_src_path: version_compile.original_sources_path,
            key_target_classpath: version_compile.original_classes_path,
            key_dependency_classpath: version_compile.get_full_classpath()
        }
