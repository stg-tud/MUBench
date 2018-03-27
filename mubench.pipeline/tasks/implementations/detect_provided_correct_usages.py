import logging
from os.path import join
from typing import Optional

from data.detector import Detector
from data.detector_run import DetectorRun
from data.misuse import Misuse
from data.misuse_compile import MisuseCompile
from data.project_version import ProjectVersion
from data.version_compile import VersionCompile
from tasks.configurations.detector_interface_configuration import key_detector_mode, \
    key_training_src_path, key_training_classes_path, key_target_src_paths, key_target_classes_paths, key_dependency_classpath


class DetectProvidedCorrectUsagesTask:
    __RUN_MODE_NAME = "detect_only"
    __DETECTOR_MODE = 1

    def __init__(self, findings_base_path: str, force_detect: bool, timeout: Optional[int], current_timestamp: int):
        self.findings_base_path = findings_base_path
        self.force_detect = force_detect
        self.timeout = timeout
        self.current_timestamp = current_timestamp

    def run(self, detector: Detector, version: ProjectVersion, version_compile: VersionCompile, misuse: Misuse,
            misuse_compile: MisuseCompile):
        run = DetectorRun(detector, version, self._get_findings_path(detector, version, misuse))

        run.ensure_executed(self._get_detector_arguments(version_compile, misuse_compile),
                            self.timeout, self.force_detect, self.current_timestamp, misuse_compile.timestamp,
                            logging.getLogger("task.detect"))

        return run

    def _get_findings_path(self, detector: Detector, version: ProjectVersion, misuse: Misuse):
        return join(self.findings_base_path, DetectProvidedCorrectUsagesTask.__RUN_MODE_NAME, detector.id,
                    version.project_id, version.version_id, misuse.misuse_id)

    @staticmethod
    def _get_detector_arguments(version_compile: VersionCompile, misuse_compile: MisuseCompile):
        return {
            key_detector_mode: DetectProvidedCorrectUsagesTask.__DETECTOR_MODE,
            key_training_src_path: misuse_compile.correct_usage_sources_path,
            key_training_classes_path: misuse_compile.correct_usage_classes_path,
            key_target_src_paths: [misuse_compile.misuse_source_path],
            key_target_classes_paths: [misuse_compile.misuse_classes_path],
            key_dependency_classpath: version_compile.get_full_classpath()
        }
