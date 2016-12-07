from nose.tools import assert_is_instance

import detectors
from benchmark.data.detectors import find_detector
from detectors.Dummy.Dummy import Dummy

_DETECTORS_PATH = detectors.__path__._path[0]


class TestDetectors:
    def test_finds_detector(self):
        detector = find_detector(_DETECTORS_PATH, "Dummy", ["-java-options-"])

        assert_is_instance(detector, Dummy)
