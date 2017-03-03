import logging
from os.path import exists
from typing import Optional, List
from urllib.error import URLError

from data.experiment import Experiment
from data.project import Project
from data.project_version import ProjectVersion
from requirements import JavaRequirement
from tasks.project_version_task import ProjectVersionTask
from utils.web_util import download_file


class Detect(ProjectVersionTask):
    def __init__(self, compiles_base_path: str, experiment: Experiment, timeout: Optional[int], force_detect: bool):
        super().__init__()
        self.force_detect = force_detect
        self.compiles_base_path = compiles_base_path
        self.experiment = experiment
        self.detector = experiment.detector
        self.timeout = timeout

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

    def process_project_version(self, project: Project, version: ProjectVersion) -> List[str]:
        logger = logging.getLogger("detect")
        run = self.experiment.get_run(version)

        if run.is_outdated() or self.force_detect:
            pass
        elif run.is_error():
            logger.info("Error in previous %s. Skipping.", run)
            return self.skip(version)
        elif run.is_success():
            logger.info("Successful previous %s. Skipping.", run)
            return self.ok()
        elif self.experiment.id == Experiment.PROVIDED_PATTERNS and not version.patterns:
            logger.info("No patterns to run with. Skipping.")
            return self.skip(version)

        run.reset()

        logger.info("Executing %s...", run)
        logger = logging.getLogger("detect.run")
        run.execute(self.compiles_base_path, self.timeout, logger)

        return self.ok() if run.is_success() else self.skip(version)
