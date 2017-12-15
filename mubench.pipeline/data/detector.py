from distutils.version import StrictVersion
from logging import Logger
from os.path import join, exists
from typing import Dict, Optional, List

from data.finding import Finding, SpecializedFinding
from data.project_version import ProjectVersion
from data.runner_interface import RunnerInterface
from utils.io import read_yaml


class Detector:
    BASE_URL = "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/detectors"
    RELEASES_FILE = "releases.yml"
    NO_MD5 = "md5 not specified"

    def __init__(self, detectors_path: str, detector_id: str, java_options: List[str],
                 requested_release: Optional[str] = None):
        self.id = detector_id
        self.base_name = detector_id.split("_", 1)[0]
        self.path = join(detectors_path, self.id)

        releases_index_path = join(self.path, Detector.RELEASES_FILE)
        release = self._get_release(releases_index_path, requested_release)
        release_tag = release.get("tag", "latest")

        if "cli_version" in release:
            cli_version = StrictVersion(release["cli_version"])
        else:
            raise ValueError("Missing CLI version for {}".format(detector_id))

        self.md5 = release.get("md5", Detector.NO_MD5)

        self.jar_path = join(self.path, self.base_name + ".jar")
        self.jar_url = "{}/{}/{}/{}.jar".format(Detector.BASE_URL, release_tag, cli_version, self.base_name)

        self.runner_interface = RunnerInterface.get(cli_version, self.jar_path, java_options)

    def _get_release(self, releases_index_file_path: str, requested_release: Optional[str]) -> Dict[str, str]:
        if exists(releases_index_file_path):
            releases = read_yaml(releases_index_file_path)
            if requested_release:
                releases = [r for r in releases if r.get("tag", "latest") == requested_release]

            if releases:
                return releases[0]
            else:
                raise ValueError("No matching {} release for {}".format(self.id, requested_release))

        raise ValueError("No releases for {}".format(self.id))

    def execute(self, version: ProjectVersion, arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        return self.runner_interface.execute(version, arguments, timeout, logger)

    def specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        raise NotImplementedError

    def __str__(self):
        return self.id
