from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals, assert_is_instance
from tests.test_utils.runner_interface_test_impl import RunnerInterfaceTestImpl

from data.detector import Detector
from data.runner_interface import NoInterface
from utils.io import remove_tree, write_yaml


class TestDetector:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-detector_")

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_defaults_on_missing_file(self):
        self.detector = Detector(self.temp_dir, "-detector-", [])

        assert_equals(None, self.detector.md5)
        assert_is_instance(self.detector.runner_interface, NoInterface)

    def test_defaults_on_no_release(self):
        self.setup_releases([])

        assert_equals(None, self.detector.md5)
        assert_is_instance(self.detector.runner_interface, NoInterface)

    def test_defaults(self):
        self.setup_releases([dict()])

        assert_equals(None, self.detector.md5)
        assert_is_instance(self.detector.runner_interface, NoInterface)

    def test_md5(self):
        self.setup_releases([{"md5": "-md5-"}])

        assert_equals("-md5-", self.detector.md5)

    def test_interface(self):
        self.setup_releases([{"cli_version": RunnerInterfaceTestImpl.TEST_VERSION}])

        assert_is_instance(self.detector.runner_interface, RunnerInterfaceTestImpl)

    def test_download_url(self):
        self.setup_releases([{"cli_version": "-version-", "tag": "-tag-"}])

        expected_url = "{}/-tag-/-version-/{}.jar".format(Detector.BASE_URL, self.detector.id)
        assert_equals(expected_url, self.detector.jar_url)

    def test_gets_requested_release(self):
        self.setup_releases([
                    {"md5": "-md5_1-", "tag": "-release_1-", "cli_version": "-version_1-"},
                    {"md5": "-md5_requested-", "tag": "-release_requested-", "cli_version": "-version_requested-"},
                    {"md5": "-md5_3-", "tag": "-release_3-", "cli_version": "-version_3-"}],
                    requested_release = "-release_requested-")

        expected_url = "{}/-release_requested-/-version_requested-/{}.jar".format(Detector.BASE_URL, self.detector.id)
        assert_equals(expected_url, self.detector.jar_url)
        assert_equals("-md5_requested-", self.detector.md5)

    def setup_releases(self, releases, requested_release = None):
        detector_id = "-detector-"
        releases_index = join(self.temp_dir, detector_id, Detector.RELEASES_FILE)
        write_yaml(releases, releases_index)
        self.detector = Detector(self.temp_dir, detector_id, [], requested_release)
