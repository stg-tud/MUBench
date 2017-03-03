from data.detector import Detector


class StubDetector(Detector):
    def __init__(self):
        super().__init__("-detectors-", "StubDetector", [])
