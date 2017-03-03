from data.detector import Detector
from data.detector_specialising.specialising_util import replace_dot_graph_with_image
from data.finding import Finding, SpecializedFinding


class MuDetect(Detector):
    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        violation = replace_dot_graph_with_image(finding, "pattern_violation", findings_path)
        target_env = replace_dot_graph_with_image(finding, "target_environment_mapping", findings_path)
        return SpecializedFinding(finding, [violation, target_env])
