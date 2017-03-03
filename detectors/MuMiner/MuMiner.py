from data.detector import Detector
from data.detector_specialising.specialising_util import replace_dot_graph_with_image
from data.finding import Finding, SpecializedFinding


class MuMiner(Detector):
    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        pattern = replace_dot_graph_with_image(finding, "pattern", findings_path)
        violation = replace_dot_graph_with_image(finding, "violation", findings_path)
        return SpecializedFinding(finding, [pattern, violation])
