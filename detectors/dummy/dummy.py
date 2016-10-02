from typing import Optional

from benchmark.data.detector import Detector
from benchmark.data.finding import Finding, SpecializedFinding


class DummyDetector(Detector):
    def __init__(self, detectors_path: str):
        super().__init__(detectors_path, "dummy", [])

    @property
    def _sort_by(self) -> Optional[str]:
        return None

    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        return SpecializedFinding(finding)
