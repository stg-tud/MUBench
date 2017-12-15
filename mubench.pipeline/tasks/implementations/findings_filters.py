from copy import deepcopy
from typing import List

from data.detector_run import DetectorRun
from data.finding import Finding
from data.misuse import Misuse


class PotentialHits:
    def __init__(self, findings: List[Finding]):
        self.findings = findings


def _to_potential_hit(misuse_id, finding: Finding):
    potential_hit = deepcopy(finding)
    potential_hit["misuse"] = misuse_id
    return potential_hit


class PotentialHitsFilterTask:
    def run(self, misuse: Misuse, detector_run: DetectorRun) -> PotentialHits:
        findings = detector_run.findings
        misuse_potential_hits = self._get_potential_hits(misuse, findings, False)
        if not misuse_potential_hits:
            misuse_potential_hits = self._get_potential_hits(misuse, findings, True)
        return PotentialHits(misuse_potential_hits)

    @staticmethod
    def _get_potential_hits(misuse: Misuse, findings: List[Finding], method_name_only: bool):
        potential_hits = []
        for finding in findings:
            if finding.is_potential_hit(misuse, method_name_only):
                potential_hits.append(_to_potential_hit(misuse.misuse_id, finding))
        return potential_hits


class AllFindingsFilterTask:
    def __init__(self, limit: int = 0):
        self.limit = limit

    def run(self, detector_run: DetectorRun) -> PotentialHits:
        findings = detector_run.findings
        top_findings = self.__get_top_findings(findings)
        potential_hits = []
        for rank, top_finding in enumerate(top_findings):
            potential_hits.append(_to_potential_hit("finding-{}".format(rank), top_finding))
        return PotentialHits(potential_hits)

    def __get_top_findings(self, findings):
        if self.limit:
            return findings[0:self.limit]
        else:
            return findings
