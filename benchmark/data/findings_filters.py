from copy import deepcopy
from typing import List

from benchmark.data.detector import Detector
from benchmark.data.finding import Finding, SpecializedFinding
from benchmark.data.misuse import Misuse


class FindingsFilter:
    def __init__(self, detector: Detector):
        self.detector = detector

    def get_potential_hits(self, findings: List[Finding], findings_path: str):
        raise NotImplementedError()


class PotentialHits(FindingsFilter):
    def __init__(self, detector: Detector, misuses: List[Misuse]):
        super().__init__(detector)
        self.misuses = misuses

    def get_potential_hits(self, findings: List[Finding], findings_path: str):
        for misuse in self.misuses:
            potential_hits = self._get_potential_hits(self.detector, misuse, findings, findings_path, False)
            if not potential_hits:
                potential_hits = self._get_potential_hits(self.detector, misuse, findings, findings_path, True)
            return potential_hits

    @staticmethod
    def _get_potential_hits(detector: Detector, misuse: Misuse, findings: List[Finding], findings_path: str,
                            method_name_only: bool):
        potential_hits = []
        for finding in findings:
            if finding.is_potential_hit(misuse, method_name_only):
                finding = deepcopy(finding)
                finding["misuse"] = misuse.id
                potential_hits.append(finding)
        potential_hits = detector.specialize_findings(findings_path, potential_hits)
        return potential_hits


class AllFindings(FindingsFilter):
    def __init__(self, detector: Detector):
        super().__init__(detector)

    def get_potential_hits(self, findings: List[Finding], findings_path: str) -> List[SpecializedFinding]:
        return self.detector.specialize_findings(findings_path, findings)
