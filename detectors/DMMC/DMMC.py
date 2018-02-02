from data.detector import Detector
from data.detector_specialising.specialising_util import format_float_value
from data.finding import Finding, SpecializedFinding


class DMMC(Detector):
    def specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        # Convert legacy property name to the name MUBench is expecting.
        if "firstcallline" in finding:
            finding["startline"] = finding.pop("firstcallline")
        
        format_float_value(finding, "strangeness")
        return SpecializedFinding(finding)
