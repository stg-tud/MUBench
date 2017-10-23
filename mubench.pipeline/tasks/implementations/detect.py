import logging
from os.path import exists
from typing import Optional, List
from urllib.error import URLError

from data.detector import Detector
from data.experiments import Experiment
from data.project_version import ProjectVersion
from data.run import Run
from utils.web_util import download_file


class DetectTask:
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

    def run(self, version: ProjectVersion) -> List[Run]:
        run = self.experiment.get_run(version)

        if run.is_outdated() or self.force_detect:
            pass
        elif run.is_error():
            self.logger.info("Error in previous %s. Skipping.", run)
            return []
        elif run.is_success():
            self.logger.info("Successful previous %s. Skipping.", run)
            return [run]

        run.reset()

        self.logger.info("Executing %s...", run)
        logger = logging.getLogger("detect.run")
        run.execute(self.compiles_base_path, self.timeout, logger)

        return [run] if run.is_success() else []
