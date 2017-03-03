import os

from nose.tools import assert_equals, assert_is_instance
from os.path import join, dirname, abspath

from data.detector import Detector
from data.detectors import find_detector

DETECTORS_PATH = join(join(dirname(abspath(__file__)), os.pardir, os.pardir, os.pardir), "detectors")


class TestDetectors:
    def test_finds_detector(self):
        detector = find_detector(DETECTORS_PATH, "Dummy", ["-java-options-"])

        assert_is_instance(detector, Detector)
        assert_equals(type(detector).__name__, "Dummy")
