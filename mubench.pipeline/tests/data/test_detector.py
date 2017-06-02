from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals, assert_is_instance
from tests.test_utils.runner_interface_test_impl import RunnerInterfaceTestImpl

from data.detector import Detector
from utils.io import remove_tree, write_yaml


class TestDetector:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-detector_")

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_defaults_on_no_release(self):
        self.setup_releases([])
        assert_equals("latest", self.detector.release_tag)
        assert_equals(None, self.detector.md5)
        assert_equals(None, self.detector.cli_version)

    def test_tag(self):
        self.setup_releases([{"tag": "-tag-"}])
        assert_equals("-tag-", self.detector.release_tag)

    def test_tag_defaults_to_latest(self):
        self.setup_releases([dict()])
        assert_equals("latest", self.detector.release_tag)

    def test_md5(self):
        self.setup_releases([{"md5": "-md5-"}])
        assert_equals("-md5-", self.detector.md5)

    def test_md5_defaults_to_none(self):
        self.setup_releases([dict()])
        assert_equals(None, self.detector.md5)

    def test_cli_version(self):
        self.setup_releases([{"cli_version": RunnerInterfaceTestImpl.TEST_VERSION}])
        assert_is_instance(self.detector.runner_interface, RunnerInterfaceTestImpl)

    def test_cli_version_defaults_to_none(self):
        self.setup_releases([dict()])
        assert_equals(None, self.detector.cli_version)

    def test_download_url(self):
        test_version = RunnerInterfaceTestImpl.TEST_VERSION
        self.setup_releases([{"tag": "-tag-", "cli_version": test_version}])

        expected_url = "{}/-tag-/{}/{}.jar".format(Detector.BASE_URL, test_version, self.detector.id)
        assert_equals(expected_url, self.detector.jar_url)

    def setup_releases(self, releases):
        detector_id = "-detector-"
        releases_index = join(self.temp_dir, detector_id, Detector.RELEASES_FILE)
        write_yaml(releases, releases_index)
        self.detector = Detector(self.temp_dir, detector_id, [])
