from data.detector import Detector
from data.detector_specialising.specialising_util import format_float_value
from data.detector_specialising.specialising_util import replace_dot_graph_with_image
from data.finding import Finding, SpecializedFinding


class GrouMiner(Detector):
    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        format_float_value(finding, "rareness")
        overlap = replace_dot_graph_with_image(finding, "overlap", findings_path)
        pattern = replace_dot_graph_with_image(finding, "pattern", findings_path)
        specialized_finding = SpecializedFinding(finding, [overlap, pattern])
        return specialized_finding
