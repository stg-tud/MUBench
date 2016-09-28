from typing import Dict, Optional

from benchmark.data import detector
from benchmark.data.detector_specialising.specialising_util import format_float_value
from benchmark.data.detector_specialising.specialising_util import replace_dot_graph_with_image


class Specialising(detector.Specialising):
    @property
    def _sort_by(self) -> Optional[str]:
        return "rareness"

    def _specialize_finding(self, findings_path: str, finding: Dict[str, str]):
        format_float_value(finding, "rareness")
        replace_dot_graph_with_image(finding, "overlap", findings_path)
        replace_dot_graph_with_image(finding, "pattern", findings_path)
        return finding
