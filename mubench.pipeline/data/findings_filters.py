from copy import deepcopy
from typing import List

from data.detector import Detector
from data.finding import Finding, SpecializedFinding
from data.misuse import Misuse


class FindingsFilter:
    def __init__(self, detector: Detector):
        self.detector = detector

    def get_potential_hits(self, findings: List[Finding]):
        raise NotImplementedError()


class PotentialHits(FindingsFilter):
    def __init__(self, detector: Detector, misuses: List[Misuse]):
        super().__init__(detector)
        self.misuses = misuses

    def get_potential_hits(self, findings: List[Finding]):
        potential_hits = []
        for misuse in self.misuses:
            misuse_potential_hits = self._get_potential_hits(misuse, findings, False)
            if not misuse_potential_hits:
                misuse_potential_hits = self._get_potential_hits(misuse, findings, True)
            potential_hits.extend(misuse_potential_hits)
        return potential_hits

    @staticmethod
    def _get_potential_hits(misuse: Misuse, findings: List[Finding], method_name_only: bool):
        potential_hits = []
        for finding in findings:
            if finding.is_potential_hit(misuse, method_name_only):
                finding = deepcopy(finding)
                finding["misuse"] = misuse.id
                potential_hits.append(finding)
        return potential_hits


class AllFindings(FindingsFilter):
    def __init__(self, detector: Detector, limit: int = 0):
        super().__init__(detector)
        self.limit = limit

    def get_potential_hits(self, findings: List[Finding]) -> List[SpecializedFinding]:
        if self.limit:
            return findings[0:self.limit]
        else:
            return findings
