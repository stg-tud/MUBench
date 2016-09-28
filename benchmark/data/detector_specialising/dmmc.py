from typing import Dict, Optional

from benchmark.data import detector
from benchmark.data.detector_specialising.customizer_util import format_float_value


class Specialising(detector.Specialising):
    @property
    def _sort_by(self) -> Optional[str]:
        return "strangeness"

    def _specialize_finding(self, findings_path: str, finding: Dict[str, str]):
        format_float_value(finding, "strangeness")
        return finding
