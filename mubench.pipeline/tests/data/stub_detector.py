from data.detector import Detector
from data.finding import Finding, SpecializedFinding
from tests.test_utils.runner_interface_test_impl import RunnerInterfaceTestImpl


class StubDetector(Detector):
    def __init__(self):
        self._get_release = lambda *_: {'cli_version': RunnerInterfaceTestImpl.TEST_VERSION}
        super().__init__("-detectors-", "StubDetector", [])

    def specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        return SpecializedFinding(finding)
