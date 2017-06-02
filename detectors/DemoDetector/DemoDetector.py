from typing import List, Optional

from data.detector import Detector
from data.finding import Finding, SpecializedFinding


class DemoDetector(Detector):
    def __init__(self, detectors_path: str, detector_id: str="DemoDetector", java_options: List[str] = None,
                requested_release: Optional[str] = None):
        super().__init__(detectors_path, detector_id, java_options or [])

    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        return SpecializedFinding(finding)
