import logging
from os.path import join
from typing import Optional

from data.detector import Detector
from data.detector_run import DetectorRun
from data.project_version import ProjectVersion
from data.version_compile import VersionCompile
from tasks.configurations.detector_interface_configuration import key_detector_mode, \
    key_target_src_paths, key_target_classes_paths, key_dependency_classpath


class DetectAllFindingsTask:
    __RUN_MODE_NAME = "mine_and_detect"
    __DETECTOR_MODE = 0

    def __init__(self, findings_base_path: str, force_detect: bool, timeout: Optional[int]):
        self.findings_base_path = findings_base_path
        self.force_detect = force_detect
        self.timeout = timeout

    def run(self, detector: Detector, version: ProjectVersion, version_compile: VersionCompile):
        run = DetectorRun(detector, version, self._get_findings_path(detector, version))

        run.ensure_executed(self._get_detector_arguments(version_compile),
                            self.timeout, self.force_detect, logging.getLogger("task.detect"))

        return run

    def _get_findings_path(self, detector: Detector, version: ProjectVersion):
        return join(self.findings_base_path, DetectAllFindingsTask.__RUN_MODE_NAME, detector.id,
                    version.project_id, version.version_id)

    @staticmethod
    def _get_detector_arguments(version_compile: VersionCompile):
        return {
            key_detector_mode: DetectAllFindingsTask.__DETECTOR_MODE,
            key_target_src_paths: version_compile.original_sources_paths,
            key_target_classes_paths: version_compile.original_classes_paths,
            key_dependency_classpath: version_compile.get_full_classpath()
        }
