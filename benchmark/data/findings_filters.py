from typing import List

from benchmark.data.detector import Detector
from benchmark.data.finding import Finding, SpecializedFinding
from benchmark.data.misuse import Misuse
from benchmark.data.project_version import ProjectVersion


class FindingsFilter:
    def __init__(self, detector: Detector):
        self.detector = detector

    def get_potential_hits(self, findings: List[Finding], findings_path: str):
        raise NotImplementedError()


class PotentialHits(FindingsFilter):
    def __init__(self, detector: Detector, misuse:Misuse):
        super().__init__(detector)
        self.misuse = misuse

    def get_potential_hits(self, findings: List[Finding], findings_path: str):
        potential_hits = self.__get_potential_hits(findings, findings_path, False)
        if not potential_hits:
            potential_hits = self.__get_potential_hits(findings, findings_path, True)
        return potential_hits

    def __get_potential_hits(self, findings: List[Finding], findings_path: str, method_name_only: bool):
        potential_hits = []
        for finding in findings:
            if finding.is_potential_hit(self.misuse, method_name_only):
                potential_hits.append(finding)
        potential_hits = self.detector.specialize_findings(findings_path, potential_hits)
        return potential_hits


class AllFindings(FindingsFilter):
    def __init__(self, detector: Detector):
        super().__init__(detector)

    def get_potential_hits(self, findings: List[Finding], findings_path: str) -> List[SpecializedFinding]:
        return self.detector.specialize_findings(findings_path, findings)

