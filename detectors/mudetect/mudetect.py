from typing import Optional

from benchmark.data.detector import Detector
from benchmark.data.detector_specialising.specialising_util import replace_dot_graph_with_image
from benchmark.data.finding import Finding, SpecializedFinding


class MuDetect(Detector):
    @property
    def _sort_by(self) -> Optional[str]:
        return "confidence"

    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        violation = replace_dot_graph_with_image(finding, "pattern_violation", findings_path)
        return SpecializedFinding(finding, [violation])
