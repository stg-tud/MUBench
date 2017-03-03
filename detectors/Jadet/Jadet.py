from data.detector import Detector
from data.detector_specialising.specialising_util import format_float_value
from data.finding import SpecializedFinding, Finding


class Jadet(Detector):
    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        format_float_value(finding, "confidence")
        format_float_value(finding, "defect_indicator")
        return SpecializedFinding(finding)
