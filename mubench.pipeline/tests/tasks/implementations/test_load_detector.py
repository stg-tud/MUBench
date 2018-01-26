from os.path import join
from tempfile import mkdtemp
from unittest.mock import patch

from nose.tools import assert_raises

from tasks.implementations.load_detector import LoadDetectorTask
from tests.data.stub_detector import StubDetector


@patch("tasks.implementations.load_detector.LoadDetectorTask._get_detector")
@patch("tasks.implementations.load_detector.LoadDetectorTask._detector_available")
@patch("tasks.implementations.load_detector.download_file")
class TestLoadDetectorTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.findings_path = join(self.temp_dir, "findings")

        self.detector = StubDetector()

        self.uut = LoadDetectorTask("", "", "", [])

    def test_downloads_detector_if_not_available(self, download_mock, detector_available_mock, get_detector_mock):
        detector_available_mock.return_value = False
        get_detector_mock.return_value = self.detector
        self.detector.md5 = ":some-md5:"

        self.uut.run()

        download_mock.assert_called_with(self.detector.jar_url, self.detector.jar_path, self.detector.md5)

    def test_aborts_download_if_detector_md5_is_missing(self, download_mock, detector_available_mock,
                                                        get_detector_mock):
        detector_available_mock.return_value = False
        get_detector_mock.return_value = self.detector

        assert_raises(ValueError, self.uut.run)
        download_mock.assert_not_called()
