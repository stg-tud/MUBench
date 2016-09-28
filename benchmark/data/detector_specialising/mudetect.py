from typing import Dict, Optional

from benchmark.data import detector
from benchmark.data.detector_specialising.customizer_util import replace_dot_graph_with_image


class Specialising(detector.Specialising):
    @property
    def _sort_by(self) -> Optional[str]:
        return "confidence"

    def _specialize_finding(self, findings_path: str, finding: Dict[str, str]):
        replace_dot_graph_with_image(finding, "pattern_violation", findings_path)
        return finding
