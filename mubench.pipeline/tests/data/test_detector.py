from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals

from data.detector import Detector
from utils.io import safe_write


class TestDetector:
    def setup(self):
        temp_dir = mkdtemp(prefix="mubench-detector_")
        self.detector = Detector(temp_dir, "-detector-", [])
        self.md5_path = join(temp_dir, "-detector-", "-detector-.md5")

    def test_md5_no_whitespace(self):
        safe_write("-md5-", self.md5_path, append=False)
        assert_equals("-md5-", self.detector.md5)
