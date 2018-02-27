import logging
from os.path import exists
from typing import List
from urllib.error import URLError

from data.detector import Detector, find_detector
from utils.web_util import download_file


class LoadDetectorTask:
    def __init__(self, detectors_path: str, detector_name: str, requested_release: str, java_options: List[str]):
        self.detectors_path = detectors_path
        self.detector_id = detector_name
        self.requested_release = requested_release
        self.java_options = java_options

    def run(self):
        logger = logging.getLogger("task.download_detector")
        detector = self._get_detector()

        if not self._detector_available(detector):
            self._download(detector, logger)

        return detector

    def _get_detector(self):
        java_options = ['-' + option for option in self.java_options]
        return find_detector(self.detectors_path, self.detector_id, java_options, self.requested_release)

    @staticmethod
    def _detector_available(detector: Detector) -> bool:
        return exists(detector.jar_path)

    @staticmethod
    def _download(detector: Detector, logger: logging.Logger):
        url = detector.jar_url
        logger.info("Loading detector '%s' from '%s'...", detector, url)
        file = detector.jar_path

        try:
            md5 = detector.md5
            if md5 == Detector.NO_MD5:
                raise ValueError("Missing MD5 for {}".format(detector.id))
            download_file(url, file, md5)
        except (FileNotFoundError, ValueError, URLError):
            logger.error("Download failed: ")
            raise
