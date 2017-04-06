from os.path import join, exists
from typing import Optional, List

from data.finding import Finding, SpecializedFinding


class Detector:
    BASE_URL = "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/detectors"
    CLI_VERSION = "v20170406"

    def __init__(self, detectors_path: str, detector_id: str, java_options: List[str]):
        self.id = detector_id
        self.base_name = detector_id.split("_", 1)[0]
        self.java_options = java_options

        self.path = join(detectors_path, self.id)
        self.jar_path = join(self.path, self.base_name + ".jar")
        self.jar_url = "{}/{}/{}.jar".format(Detector.BASE_URL, Detector.CLI_VERSION, self.base_name)
        self.md5_path = join(self.path, self.base_name + ".md5")

    @property
    def md5(self) -> Optional[str]:
        md5_file = self.md5_path
        md5 = None

        if exists(md5_file):
            with open(md5_file) as file:
                md5 = file.read().strip()

        return md5

    def specialize_findings(self, findings_path: str, findings: List[Finding]) -> List[SpecializedFinding]:
        return [self._specialize_finding(findings_path, finding) for finding in findings]

    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        raise NotImplementedError

    def __str__(self):
        return self.id
