from data.detector import Detector
from tests.test_utils.java_interface_test_impl import JavaInterfaceTestImpl

class StubDetector(Detector):
    def __init__(self):
        super().__init__("-detectors-", "StubDetector", [], cli_version=JavaInterfaceTestImpl.TEST_VERSION)
