from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals, assert_is_instance, assert_raises

from data.detector import Detector
from tests.test_utils.runner_interface_test_impl import RunnerInterfaceTestImpl
from utils.io import remove_tree, write_yaml


class TestDetector:
    def setup(self):
        self.detector_id = "-detector-"
        self.temp_dir = mkdtemp(prefix="mubench-detector_")

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_raises_on_missing_file(self):
        assert_raises(ValueError, Detector, self.temp_dir, "-detector-", [])

    def test_raises_value_error_on_no_release(self):
        self.setup_releases([])
        assert_raises(ValueError, Detector, self.temp_dir, self.detector_id, [])

    def test_md5(self):
        self.setup_releases([{"md5": "-md5-",
            "cli_version": RunnerInterfaceTestImpl.TEST_VERSION}])
        detector = Detector(self.temp_dir, self.detector_id, [])

        assert_equals("-md5-", detector.md5)

    def test_md5_defaults_to_none(self):
        self.setup_releases([{"cli_version": RunnerInterfaceTestImpl.TEST_VERSION}])
        detector = Detector(self.temp_dir, self.detector_id, [])
        assert_equals(detector.md5, Detector.NO_MD5)

    def test_interface(self):
        self.setup_releases([{"cli_version": RunnerInterfaceTestImpl.TEST_VERSION, "md5": "-md5-"}])
        detector = Detector(self.temp_dir, self.detector_id, [])

        assert_is_instance(detector.runner_interface, RunnerInterfaceTestImpl)

    def test_raises_on_missing_cli_version(self):
        self.setup_releases([{"md5": "-md5-"}])
        assert_raises(ValueError, Detector, self.temp_dir, self.detector_id, [])

    def test_download_url(self):
        self.setup_releases(
                [{"cli_version": RunnerInterfaceTestImpl.TEST_VERSION, "tag": "-tag-", "md5": "-md5-"}])
        detector = Detector(self.temp_dir, self.detector_id, [])

        expected_url = "{}/-tag-/{}/{}.jar".format(Detector.BASE_URL,
                RunnerInterfaceTestImpl.TEST_VERSION, self.detector_id)
        assert_equals(expected_url, detector.jar_url)

    def test_gets_requested_release(self):
        self.setup_releases([
                    {"md5": "-md5_1-", "tag": "-release_1-", "cli_version": "0.0.0"},
                    {"md5": "-md5_requested-", "tag": "-release_requested-",
                        "cli_version": RunnerInterfaceTestImpl.TEST_VERSION},
                    {"md5": "-md5_3-", "tag": "-release_3-", "cli_version": "0.0.2"}])
        detector = Detector(self.temp_dir, self.detector_id, [], "-release_requested-")

        expected_url = "{}/-release_requested-/{}/{}.jar".format(Detector.BASE_URL,
                RunnerInterfaceTestImpl.TEST_VERSION, self.detector_id)
        assert_equals(expected_url, detector.jar_url)
        assert_equals("-md5_requested-", detector.md5)

    def test_raises_on_no_matching_release(self):
        self.setup_releases([{"md5": "-md5-", "tag": "-release-", "cli_version": "0.0.1"}])
        assert_raises(ValueError, Detector, self.temp_dir, self.detector_id, [], "-unavailable_release-")

    def test_release_is_case_insensitive(self):
        self.setup_releases([
            {"md5": "-md5_1-", "tag": "-release_1-", "cli_version": "-version-"},
            {"md5": "-md5_requested-", "tag": "RELEASE_REQUESTED",
             "cli_version": RunnerInterfaceTestImpl.TEST_VERSION},
            {"md5": "-md5_3-", "tag": "-release_3-", "cli_version": "-version-"}])
        detector = Detector(self.temp_dir, self.detector_id, [], "Release_Requested")

        expected_url = "{}/release_requested/{}/{}.jar".format(Detector.BASE_URL,
                                                               RunnerInterfaceTestImpl.TEST_VERSION, self.detector_id)
        assert_equals(expected_url, detector.jar_url)
        assert_equals("-md5_requested-", detector.md5)

    def setup_releases(self, releases):
        releases_index = join(self.temp_dir, self.detector_id, Detector.RELEASES_FILE)
        write_yaml(releases, releases_index)
