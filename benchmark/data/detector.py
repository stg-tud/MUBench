from copy import deepcopy
from os.path import join, exists
from typing import Optional, List

from benchmark.data.finding import Finding, SpecializedFinding


class Detector:
    def __init__(self, detectors_path: str, detector_id: str, java_options: List[str]):
        self.id = detector_id
        self.java_options = java_options

        self.path = join(detectors_path, self.id)
        self.jar_path = join(self.path, self.id + ".jar")
        self.jar_url = "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/{}.jar".format(self.id)
        self.md5_path = join(self.path, self.id + ".md5")

    @property
    def md5(self) -> Optional[str]:
        md5_file = self.md5_path
        md5 = None

        if exists(md5_file):
            with open(md5_file) as file:
                md5 = file.read()

        return md5

    def specialize_findings(self, findings_path: str, findings: List[Finding]) -> List[SpecializedFinding]:
        findings = self._sort_findings(findings)
        specialized_findings = []
        for finding in findings:
            specialized_findings.append(self._specialize_finding(findings_path, finding))
        return specialized_findings

    def _sort_findings(self, findings: List[Finding]) -> List[Finding]:
        findings = deepcopy(findings)
        sort_by = self._sort_by
        if sort_by:
            findings.sort(key=lambda f: float(f[sort_by]), reverse=True)
        return findings

    @property
    def _sort_by(self) -> Optional[str]:
        raise NotImplementedError

    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        raise NotImplementedError

    def __str__(self):
        return self.id


