from typing import Dict, Optional

from benchmark.data.detector import Detector
from benchmark.data.detector_specialising.specialising_util import format_float_value


class Dmmc(Detector):
    @property
    def _sort_by(self) -> Optional[str]:
        return "strangeness"

    def _specialize_finding(self, findings_path: str, finding: Dict[str, str]):
        format_float_value(finding, "strangeness")
        return finding
