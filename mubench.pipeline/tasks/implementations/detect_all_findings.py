import logging
from os.path import exists, join
from typing import Optional, List
from urllib.error import URLError

from data.detector import Detector
from data.detector_execution import DetectorExecution
from data.findings_filters import AllFindings
from data.project_version import ProjectVersion
from data.version_compile import VersionCompile
from tasks.configurations.detector_interface_configuration import key_findings_file, key_run_file, key_detector_mode, \
    key_target_src_path, key_target_classpath, key_dependency_classpath
from utils.web_util import download_file

RUN_MODE_NAME = "mine_and_detect"
DETECTOR_MODE = 0


class DetectAllFindingsTask:
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    def __init__(self, compiles_base_path: str, findings_base_path: str, detector: Detector, timeout: Optional[int],
                 force_detect: bool, limit: Optional[int]):
        super().__init__()
        self.force_detect = force_detect
        self.compiles_base_path = compiles_base_path
        self.findings_base_path = findings_base_path
        self.detector = detector
        self.timeout = timeout
        self.limit = limit

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

    def run(self, version: ProjectVersion, version_compile: VersionCompile) -> List[DetectorExecution]:
        run = self._get_execution(version)

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
        run.execute(self._get_detector_arguments(self._get_findings_file_path(version),
                                                 self._get_run_file_path(version),
                                                 version_compile),
                    self.timeout, logger)

        if not run.is_success():
            raise UserWarning("Run {} failed.".format(str(run)))

        return run

    def _get_execution(self, version: ProjectVersion) -> DetectorExecution:
        findings_filter = AllFindings(self.limit)
        return DetectorExecution(self.detector, version, self._get_findings_path(version), findings_filter,
                                 self._get_findings_file_path(version), self._get_run_file_path(version))

    def _get_run_file_path(self, version: ProjectVersion):
        return join(self._get_findings_path(version), self.RUN_FILE)

    def _get_findings_path(self, version: ProjectVersion):
        return join(self.findings_base_path,
                    RUN_MODE_NAME, self.detector.id,
                    version.project_id, version.version_id)

    def _get_findings_file_path(self, version: ProjectVersion):
        return join(self._get_findings_path(version), self.FINDINGS_FILE)

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
