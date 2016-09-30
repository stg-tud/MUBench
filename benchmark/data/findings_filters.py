from typing import List

from benchmark.data.detector import Detector
from benchmark.data.finding import Finding
from benchmark.data.misuse import Misuse
from benchmark.data.project_version import ProjectVersion


class FindingsFilter:
    def __init__(self, detector: Detector, ):
        self.detector = detector

    def get_potential_hits(self, findings: List[Finding]):
        raise NotImplementedError()


class PotentialHits(FindingsFilter):
    def __init__(self, detector: Detector, misuse:Misuse):
        super().__init__(detector)
        self.misuse = misuse

    def get_potential_hits(self, findings: List[Finding]):
        potential_hits = self.__get_potential_hits(findings, False)
        if not potential_hits:
            potential_hits = self.__get_potential_hits(findings, True)
        return potential_hits

    def __get_potential_hits(self, findings: List[Finding], method_name_only: bool):
        potential_hits = []
        for finding in findings:
            if finding.is_potential_hit(self.misuse, method_name_only):
                potential_hits.append(finding)
        return potential_hits


class AllFindings(FindingsFilter):
    def __init__(self, detector: Detector, version: ProjectVersion):
        super().__init__(detector)
        self.version = version

    def get_potential_hits(self, findings: List[Finding]):
        return [self.__to_misuse(finding) for finding in findings]

    def __to_misuse(self, finding: Finding):
        misuse = Misuse("", self.version.project_id, "finding" + finding["id"])
        misuse.location.file = finding["file"]
        misuse.location.method = finding["method"]
        return misuse

