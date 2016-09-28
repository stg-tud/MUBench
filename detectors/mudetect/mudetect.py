from typing import Dict, Optional

from benchmark.data.detector import Detector
from benchmark.data.detector_specialising.specialising_util import replace_dot_graph_with_image


class MuDetect(Detector):
    @property
    def _sort_by(self) -> Optional[str]:
        return "confidence"

    def _specialize_finding(self, findings_path: str, finding: Dict[str, str]):
        violation = replace_dot_graph_with_image(finding, "pattern_violation", findings_path)
        self.files_to_upload.append(violation)
        return finding
