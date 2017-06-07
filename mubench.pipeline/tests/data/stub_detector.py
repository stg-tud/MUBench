from data.detector import Detector
from tests.test_utils.runner_interface_test_impl import RunnerInterfaceTestImpl

class StubDetector(Detector):
    def __init__(self):
        self._get_release = lambda *_: {'tag': 'latest', 'md5': None, 'cli_version': RunnerInterfaceTestImpl.TEST_VERSION}
        super().__init__("-detectors-", "StubDetector", [])
