from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals

from data.detector import Detector
from utils.io import safe_write


class TestDetector:
    def test_md5_no_whitespace(self):
        temp_dir = mkdtemp(prefix="mubench-detector_")
        md5_path = join(temp_dir, "test.md5")
        safe_write("-test-md5-", md5_path, append=False)

        detector = Detector("-path-", "id", [])
        detector.md5_path = md5_path

        assert_equals("-test-md5-", detector.md5)
