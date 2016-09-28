from typing import Dict, Optional

from benchmark.data.detector import Detector
from benchmark.data.detector_specialising.specialising_util import format_float_value
from benchmark.data.detector_specialising.specialising_util import replace_dot_graph_with_image


class Grouminer(Detector):
    @property
    def _sort_by(self) -> Optional[str]:
        return "rareness"

    def _specialize_finding(self, findings_path: str, finding: Dict[str, str]):
        format_float_value(finding, "rareness")
        overlap = replace_dot_graph_with_image(finding, "overlap", findings_path)
        pattern = replace_dot_graph_with_image(finding, "pattern", findings_path)
        self.files_to_upload.extend([overlap, pattern])
        return finding
