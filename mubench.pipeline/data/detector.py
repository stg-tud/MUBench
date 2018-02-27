from distutils.version import StrictVersion
from logging import Logger
from os import listdir
from os.path import join, isdir
from typing import Dict, Optional, List

from data.project_version import ProjectVersion
from data.runner_interface import RunnerInterface
from utils.io import read_yaml_if_exists


class Detector:
    BASE_URL = "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/detectors"
    RELEASES_FILE = "releases.yml"
    NO_MD5 = "md5 not specified"
    DEFAULT_RELEASE = "latest"

    def __init__(self, detectors_path: str, detector_id: str, java_options: List[str], requested_release: str):
        self.id = detector_id
        self.base_name = detector_id.split("_", 1)[0]
        self.path = join(detectors_path, self.id)

        releases_index_path = join(self.path, Detector.RELEASES_FILE)
        release = self._get_release(releases_index_path, requested_release)
        release_tag = release["tag"]

        if "cli_version" in release:
            cli_version = StrictVersion(release["cli_version"])
        else:
            raise ValueError("Missing CLI version for {}".format(detector_id))

        self.md5 = release.get("md5", Detector.NO_MD5)

        self.jar_path = join(self.path, self.base_name + ".jar")
        self.jar_url = "{}/{}/{}/{}.jar".format(Detector.BASE_URL, release_tag, cli_version, self.base_name)

        self.runner_interface = RunnerInterface.get(cli_version, self.jar_path, java_options)

    def _get_release(self, releases_index_file_path: str, requested_release: str) -> Dict[str, str]:
        releases = self.__load_release_file(releases_index_file_path)

        for release in releases:
            release["tag"] = release.get("tag", "").lower()

        matching_releases = [r for r in releases if r["tag"] == requested_release]
        if matching_releases:
            release = matching_releases[0]
        elif releases and requested_release == Detector.DEFAULT_RELEASE:
            release = releases[0]
            if not release["tag"]:
                release["tag"] = Detector.DEFAULT_RELEASE
        else:
            raise ValueError("No (matching) {} release for {}".format(self.id, requested_release))

        return release

    @staticmethod
    def __load_release_file(releases_index_file_path):
        return read_yaml_if_exists(releases_index_file_path)

    def execute(self, version: ProjectVersion, arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        return self.runner_interface.execute(version, arguments, timeout, logger)

    def __str__(self):
        return self.id


def find_detector(detectors_path: str, detector_id_prefix: str, java_options: List[str], release_tag: str):
    detector_id = _find_detector_id(detector_id_prefix, detectors_path)
    return Detector(detectors_path, detector_id, java_options, release_tag)


def _find_detector_id(detector_id_prefix, detectors_path) -> str:
    available_detector_ids = get_available_detector_ids(detectors_path)
    detector_ids = [id for id in available_detector_ids if id == detector_id_prefix] or \
                   [id for id in available_detector_ids if id.startswith(detector_id_prefix)]
    if not detector_ids:
        raise ValueError("no detector with id '{}'".format(detector_id_prefix))
    elif len(detector_ids) > 1:
        raise ValueError("more than one detector matching id prefix '{}': {}".format(detector_id_prefix, detector_ids))
    else:
        return detector_ids[0]


def get_available_detector_ids(detectors_path):
    return [dir_name for dir_name in listdir(detectors_path) if isdir(join(detectors_path, dir_name))]
