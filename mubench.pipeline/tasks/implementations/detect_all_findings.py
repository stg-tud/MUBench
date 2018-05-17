import logging
from os.path import join
from typing import Optional, List

from data.detector import Detector
from data.detector_run import DetectorRun
from data.project_version import ProjectVersion
from data.version_compile import VersionCompile
from tasks.configurations.detector_interface_configuration import key_detector_mode, \
    key_target_src_paths, key_target_classes_paths, key_dependency_classpath, key_training_src_path
from tasks.implementations.crossproject_prepare import CrossProjectSourcesPaths


class DetectAllFindingsTask:
    __RUN_MODE_NAME = "mine_and_detect"
    __DETECTOR_MODE = 0

    def __init__(self, findings_base_path: str, force_detect: bool, timeout: Optional[int], current_timestamp: int):
        self.findings_base_path = findings_base_path
        self.force_detect = force_detect
        self.timeout = timeout
        self.current_timestamp = current_timestamp

    def run(self, detector: Detector, version: ProjectVersion, version_compile: VersionCompile,
            xp_sources_paths: CrossProjectSourcesPaths):
        run = self._get_detector_run(detector, version)

        run.ensure_executed(self._get_detector_arguments(version_compile, xp_sources_paths.get()),
                            self.timeout, self.force_detect, self.current_timestamp, version_compile.timestamp,
                            logging.getLogger("task.detect"))

        return run

    def _get_detector_run(self, detector, version):
        return DetectorRun(detector, version, self._get_findings_path(detector, version))

    def _get_findings_path(self, detector: Detector, version: ProjectVersion):
        return join(self.findings_base_path, DetectAllFindingsTask.__RUN_MODE_NAME, detector.id,
                    version.project_id, version.version_id)

    @staticmethod
    def _get_detector_arguments(version_compile: VersionCompile, xp_sources_paths: List[str]):
        detector_args = {key_detector_mode: DetectAllFindingsTask.__DETECTOR_MODE,
                         key_target_src_paths: version_compile.original_sources_paths,
                         key_target_classes_paths: version_compile.original_classes_paths,
                         key_dependency_classpath: version_compile.get_full_classpath()}
        if xp_sources_paths:
            detector_args[key_training_src_path] = xp_sources_paths
        return detector_args
