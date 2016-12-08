from typing import Optional

from benchmark.data.detector import Detector
from benchmark.data.detector_specialising.specialising_util import format_float_value
from benchmark.data.finding import Finding, SpecializedFinding


class DMMC(Detector):
    @property
    def _sort_by(self) -> Optional[str]:
        return "strangeness"

    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        format_float_value(finding, "strangeness")
        return SpecializedFinding(finding)
