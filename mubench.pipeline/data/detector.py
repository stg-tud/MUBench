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

    def __init__(self, detectors_path: str, detector_id: str, java_options: List[str]):
        self.id = detector_id
        self.base_name = detector_id.split("_", 1)[0]
        self.path = join(detectors_path, self.id)

        releases_index_path = join(self.path, Detector.RELEASES_FILE)
        release_info = self._get_release_info(releases_index_path)
        self.release_tag = release_info.get("tag", "latest")
        self.md5 = release_info.get("md5", None)
        self.cli_version = release_info.get("cli_version", None)

        self.jar_path = join(self.path, self.base_name + ".jar")
        self.jar_url = "{}/{}/{}/{}.jar".format(Detector.BASE_URL, self.release_tag, self.cli_version, self.base_name)
        self.runner_interface = RunnerInterface.get(self.cli_version, self.jar_path, java_options)

    def _get_release_info(self, releases_index_file_path: str) -> Dict[str, str]:
        if exists(releases_index_file_path):
            releases = read_yaml(releases_index_file_path)
            if len(releases) > 0:
                return releases[0]
        return dict()

    def execute(self, version: ProjectVersion, arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        return self.runner_interface.execute(version, arguments, timeout, logger)

    def specialize_findings(self, findings_path: str, findings: List[Finding]) -> List[SpecializedFinding]:
        return [self._specialize_finding(findings_path, finding) for finding in findings]

    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        raise NotImplementedError

    def __str__(self):
        return self.id
