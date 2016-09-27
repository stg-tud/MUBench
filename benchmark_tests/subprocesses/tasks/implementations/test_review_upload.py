import json
from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark.subprocesses.tasks.implementations.detect import Run, Result
from benchmark.subprocesses.tasks.implementations.review_upload import ReviewUpload, Request
from benchmark.utils.io import remove_tree
from benchmark_tests.data.test_misuse import create_misuse
from benchmark_tests.test_utils.data_util import create_project, create_version

TEST_DETECTOR_ID = "-detector-"
TEST_DATASET = "-dataset-"
TEST_PROJECT_ID = "-p-"
TEST_VERSION_ID = "-v-"
TEST_MISUSE_ID = "-m-"


# noinspection PyAttributeOutsideInit
class TestReviewUploadEx1:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench_test-review-prepare")

        self.findings_path = join(self.temp_dir, "findings")
        self.dataset = TEST_DATASET
        self.checkout_base_dir = join(self.temp_dir, "checkouts")

        self.project = create_project(TEST_PROJECT_ID)
        self.misuse = create_misuse(TEST_MISUSE_ID, project=self.project)
        self.version = create_version(TEST_VERSION_ID, project=self.project, misuses=[self.misuse])

        self.potential_hits = []

        self.detector = Detector(join(self.temp_dir, "detectors"), TEST_DETECTOR_ID)
        self.experiment = Experiment(Experiment.PROVIDED_PATTERNS, self.detector, self.findings_path,
                                     join(self.temp_dir, "reviews"))
        self.test_run = Run("")
        self.test_run.result = Result.success
        self.test_run.get_potential_hits = lambda m: self.potential_hits
        self.experiment.get_run = lambda v: self.test_run

        self.uut = ReviewUpload(self.experiment, self.dataset, self.checkout_base_dir)

        self.post_url = None
        self.post_data = None
        self.post_files = None

        def post_mock(url, data, files):
            self.post_url = url
            self.post_data = data
            self.post_files = files

        self.uut.post = post_mock

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_creates_request_data(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual_data = self.uut.request_data
        actual_files = self.uut.request_files
        assert_equals(1, len(actual_data))
        assert_equals(0, len(actual_files))

    def test_skips_if_no_result(self):
        self.test_run.result = None

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual_data = self.uut.request_data
        actual_files = self.uut.request_files
        assert_equals(0, len(actual_data))
        assert_equals(0, len(actual_files))

    def test_request_contains_dataset(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_DATASET, actual.dataset)

    def test_request_contains_detector_name(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_DETECTOR_ID, actual.detector_name)

    def test_request_contains_project_id(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_PROJECT_ID, actual.project)

    def test_request_contains_version_id(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_VERSION_ID, actual.version)

    def test_request_contains_potential_hits(self):
        self.potential_hits = [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific1-"},
                               {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific2-"}]

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(self.potential_hits, actual.findings)

    def test_post_url(self):
        self.uut.request_data = [Request(TEST_DATASET, self.detector, self.project, self.version,
                                         [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific1-"},
                                          {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific2-"}])]

        self.uut.end()

        actual_url = self.post_url
        assert_equals(actual_url, "/upload/ex1")

    def test_post_data(self):
        self.uut.request_data = [Request(TEST_DATASET, self.detector, self.project, self.version,
                                         [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific1-"},
                                          {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific2-"}])]

        self.uut.end()

        actual_data = self.post_data
        assert_equals(actual_data, json.dumps([{"detector_name": "-detector-", "dataset": "-dataset-",
                                                "project": "-p-", "version": "-v-",
                                                "findings": [
                                                    {"id": "-1-", "detector-specific": "-specific1-",
                                                     "misuse": "-p-.-m1-"},
                                                    {"id": "-2-", "detector-specific": "-specific2-",
                                                     "misuse": "-p-.-m2-"}]}], sort_keys=True))


# noinspection PyAttributeOutsideInit
class TestReviewUploadEx2:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench_test-review-prepare")

        self.findings_path = join(self.temp_dir, "findings")
        self.dataset = TEST_DATASET
        self.checkout_base_dir = join(self.temp_dir, "checkouts")

        self.project = create_project(TEST_PROJECT_ID)
        self.misuse = create_misuse(TEST_MISUSE_ID, project=self.project)
        self.version = create_version(TEST_VERSION_ID, project=self.project, misuses=[self.misuse])

        self.potential_hits = []

        self.detector = Detector(join(self.temp_dir, "detectors"), TEST_DETECTOR_ID)
        self.experiment = Experiment(Experiment.TOP_FINDINGS, self.detector, self.findings_path,
                                     join(self.temp_dir, "reviews"))
        self.test_run = Run("")
        self.test_run.result = Result.success
        self.test_run.get_potential_hits = lambda m: self.potential_hits
        self.experiment.get_run = lambda v: self.test_run

        self.uut = ReviewUpload(self.experiment, self.dataset, self.checkout_base_dir)

        self.post_url = None
        self.post_data = None
        self.post_files = None

        def post_mock(url, data, files):
            self.post_url = url
            self.post_data = data
            self.post_files = files

        self.uut.post = post_mock

    def test_creates_request_data(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual_data = self.uut.request_data
        actual_files = self.uut.request_files
        assert_equals(1, len(actual_data))
        assert_equals(0, len(actual_files))

    def test_skips_if_no_result(self):
        self.test_run.result = None

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual_data = self.uut.request_data
        actual_files = self.uut.request_files
        assert_equals(0, len(actual_data))
        assert_equals(0, len(actual_files))

    def test_request_contains_dataset(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_DATASET, actual.dataset)

    def test_request_contains_detector_name(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_DETECTOR_ID, actual.detector_name)

    def test_request_contains_project_id(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_PROJECT_ID, actual.project)

    def test_request_contains_version_id(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_VERSION_ID, actual.version)

    def test_post_url(self):
        self.uut.end()

        actual_url = self.post_url
        assert_equals(actual_url, "/upload/ex2")

    def test_request_contains_findings(self):
        self.uut.request_data = [Request(TEST_DATASET, self.detector, self.project, self.version,
                                         [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific1-"},
                                          {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific2-"}])]

        self.uut.end()

        actual_url = self.post_url
        assert_equals(actual_url, "/upload/ex2")


# noinspection PyAttributeOutsideInit
class TestReviewUploadEx3:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench_test-review-prepare")

        self.findings_path = join(self.temp_dir, "findings")
        self.dataset = TEST_DATASET
        self.checkout_base_dir = join(self.temp_dir, "checkouts")

        self.project = create_project(TEST_PROJECT_ID)
        self.misuse = create_misuse(TEST_MISUSE_ID, project=self.project)
        self.version = create_version(TEST_VERSION_ID, project=self.project, misuses=[self.misuse])

        self.potential_hits = []

        self.detector = Detector(join(self.temp_dir, "detectors"), TEST_DETECTOR_ID)
        self.experiment = Experiment(Experiment.BENCHMARK, self.detector, self.findings_path,
                                     join(self.temp_dir, "reviews"))
        self.test_run = Run("")
        self.test_run.result = Result.success
        self.test_run.get_potential_hits = lambda m: self.potential_hits
        self.experiment.get_run = lambda v: self.test_run

        self.uut = ReviewUpload(self.experiment, self.dataset, self.checkout_base_dir)

        self.post_url = None
        self.post_data = None
        self.post_files = None

        def post_mock(url, data, files):
            self.post_url = url
            self.post_data = data
            self.post_files = files

        self.uut.post = post_mock

    def test_creates_request_data(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual_data = self.uut.request_data
        actual_files = self.uut.request_files
        assert_equals(1, len(actual_data))
        assert_equals(0, len(actual_files))

    def test_skips_if_no_result(self):
        self.test_run.result = None

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual_data = self.uut.request_data
        actual_files = self.uut.request_files
        assert_equals(0, len(actual_data))
        assert_equals(0, len(actual_files))

    def test_request_contains_dataset(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_DATASET, actual.dataset)

    def test_request_contains_detector_name(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_DETECTOR_ID, actual.detector_name)

    def test_request_contains_project_id(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_PROJECT_ID, actual.project)

    def test_request_contains_version_id(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(TEST_VERSION_ID, actual.version)

    def test_request_contains_potential_hits(self):
        self.potential_hits = [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific1-"},
                               {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific2-"}]

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(self.potential_hits, actual.findings)

    def test_post_url(self):
        self.uut.request_data = [Request(TEST_DATASET, self.detector, self.project, self.version,
                                         [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific1-"},
                                          {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific2-"}])]

        self.uut.end()

        actual_url = self.post_url
        assert_equals(actual_url, "/upload/ex3")

    def test_post_data(self):
        self.uut.request_data = [Request(TEST_DATASET, self.detector, self.project, self.version,
                                         [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific1-"},
                                          {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific2-"}])]

        self.uut.end()

        actual_data = self.post_data
        assert_equals(actual_data, json.dumps([{"detector_name": "-detector-", "dataset": "-dataset-",
                                                "project": "-p-", "version": "-v-",
                                                "findings": [
                                                    {"id": "-1-", "detector-specific": "-specific1-",
                                                     "misuse": "-p-.-m1-"},
                                                    {"id": "-2-", "detector-specific": "-specific2-",
                                                     "misuse": "-p-.-m2-"}]}], sort_keys=True))
