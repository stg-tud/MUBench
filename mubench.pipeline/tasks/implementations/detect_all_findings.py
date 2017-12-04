import logging
from os.path import join
from typing import Optional

from data.detector import Detector
from data.detector_run import DetectorRun
from data.project_version import ProjectVersion
from data.version_compile import VersionCompile
from tasks.configurations.detector_interface_configuration import key_findings_file, key_run_file, key_detector_mode, \
    key_target_src_path, key_target_classpath, key_dependency_classpath


class DetectAllFindingsTask:
    __RUN_MODE_NAME = "mine_and_detect"
    __DETECTOR_MODE = 0
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    def __init__(self, findings_base_path: str, force_detect: bool, timeout: Optional[int]):
        self.findings_base_path = findings_base_path
        self.force_detect = force_detect
        self.timeout = timeout

    def run(self, detector: Detector, version: ProjectVersion, version_compile: VersionCompile):
        findings_path = self._get_findings_path(detector, version)
        findings_file_path = self._get_findings_file_path(findings_path)
        run_file_path = self._get_run_file_path(findings_path)
        run = self._get_run(detector, version, findings_path, findings_file_path, run_file_path)

        run.ensure_executed(self._get_detector_arguments(findings_file_path, run_file_path, version_compile),
                            self.timeout, self.force_detect, logging.getLogger("task.detect"))

        return run

    def _get_run(self, detector: Detector, version: ProjectVersion, findings_path, findings_file_path, run_file_path):
        return DetectorRun(detector, version, findings_path, findings_file_path, run_file_path)

    def _get_run_file_path(self, findings_path):
        return join(findings_path, self.RUN_FILE)

    def _get_findings_file_path(self, findings_path):
        return join(findings_path, self.FINDINGS_FILE)

    def _get_findings_path(self, detector: Detector, version: ProjectVersion):
        return join(self.findings_base_path, DetectAllFindingsTask.__RUN_MODE_NAME, detector.id,
                    version.project_id, version.version_id)

    @staticmethod
    def _get_detector_arguments(findings_file_path: str, run_file_path: str, version_compile: VersionCompile):
        return {
            key_findings_file: findings_file_path,
            key_run_file: run_file_path,
            key_detector_mode: DetectAllFindingsTask.__DETECTOR_MODE,
            key_target_src_path: version_compile.original_sources_path,
            key_target_classpath: version_compile.original_classes_path,
            key_dependency_classpath: version_compile.get_full_classpath()
        }
