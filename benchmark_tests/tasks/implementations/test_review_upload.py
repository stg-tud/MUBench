import json
from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.data.detector_execution import MineAndDetectExecution
from benchmark.data.experiment import Experiment
from benchmark.data.finding import SpecializedFinding
from benchmark.data.findings_filters import PotentialHits
from benchmark.data.run import Run
from benchmark.tasks.implementations.review_upload import ReviewUpload, RequestData
from benchmark.utils.io import remove_tree, create_file
from benchmark_tests.data.test_misuse import create_misuse
from benchmark_tests.test_utils.data_util import create_project, create_version
from detectors.dummy.dummy import DummyDetector

TEST_DATASET = "-dataset-"
TEST_PROJECT_ID = "-p-"
TEST_VERSION_ID = "-v-"
TEST_MISUSE_ID = "-m-"


# noinspection PyAttributeOutsideInit
class TestReviewUpload:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench_test-review-prepare")

        self.findings_path = join(self.temp_dir, "findings")
        self.dataset = TEST_DATASET

        self.project = create_project(TEST_PROJECT_ID)
        self.misuse = create_misuse(TEST_MISUSE_ID, project=self.project)
        self.version = create_version(TEST_VERSION_ID, project=self.project, misuses=[self.misuse])

        self.potential_hits = []

        self.detector = DummyDetector(join(self.temp_dir, "detectors"))
        self.experiment = Experiment(Experiment.PROVIDED_PATTERNS, self.detector, self.findings_path,
                                     join(self.temp_dir, "reviews"))
        self.test_run = Run([MineAndDetectExecution(self.detector, self.version, self.findings_path,
                                                    PotentialHits(self.detector, self.misuse))])
        self.test_run.is_success = lambda: True
        self.test_run.results = lambda: self.potential_hits
        self.experiment.get_run = lambda v: self.test_run

        self.uut = ReviewUpload(self.experiment, self.dataset)

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

        actual_data = self.uut.data
        assert_equals(1, len(actual_data))

    def test_request_contains_dataset(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.data[0]
        assert_equals(TEST_DATASET, actual.dataset)

    def test_request_contains_detector_name(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.data[0]
        assert_equals(self.detector.id, actual.detector_name)

    def test_request_contains_project_id(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.data[0]
        assert_equals(TEST_PROJECT_ID, actual.project)

    def test_request_contains_version_id(self):
        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.data[0]
        assert_equals(TEST_VERSION_ID, actual.version)

    def test_request_contains_potential_hits(self):
        self.potential_hits = [{"id": "-1-", "misuse": "-p-.-m1-", "detector_specific": "-specific1-"},
                               {"id": "-2-", "misuse": "-p-.-m2-", "detector_specific": "-specific2-"}]

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.data[0]
        assert_equals(self.potential_hits, actual.findings)

    def test_post_url(self):
        self.uut.data = [RequestData(TEST_DATASET, self.detector, self.project, self.version, [])]

        self.uut.end()

        actual_url = self.post_url
        assert_equals(actual_url, "/upload/ex1")

    def test_post_data(self):
        self.uut.data = [RequestData(TEST_DATASET, self.detector, self.project, self.version, [
            SpecializedFinding({"id": "-1-", "detector_specific": "-specific-", "misuse": "-p-.-m-"})])]

        self.uut.end()

        actual_data = self.post_data
        assert_equals(json.dumps([{"detector_name": self.detector.id, "dataset": TEST_DATASET,
                                   "project": "-p-", "version": "-v-",
                                   "findings": [
                                       {"id": "-1-", "detector_specific": "-specific-",
                                        "misuse": "-p-.-m-"}]}], sort_keys=True), actual_data)

    def test_post_files(self):
        files = ['-p-.-v-.overlap.png']
        finding = SpecializedFinding({}, files)
        test_data = RequestData(TEST_DATASET, self.detector, self.project, self.version,
                                [finding])
        self.uut.data = [test_data]

        self.uut.end()

        actual_files = self.post_files
        assert_equals(files, actual_files)


class TestRequestFileTuple:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-test-request_file_tuple_")
        self.file = join(self.temp_dir, "file.png")
        create_file(self.file)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_create_request_file_tuple_name(self):
        actual_tuple = ReviewUpload._get_request_file_tuple(self.file)

        assert_equals("file.png", actual_tuple[0])
        assert_equals("file.png", actual_tuple[1][0])

    def test_create_request_file_tuple_stream(self):
        actual_tuple = ReviewUpload._get_request_file_tuple(self.file)

        assert_equals(self.file, actual_tuple[1][1].name)
        assert_equals('rb', actual_tuple[1][1].mode)

    def test_create_request_file_tuple_mime_type(self):
        actual_tuple = ReviewUpload._get_request_file_tuple(self.file)

        assert_equals('image/png', actual_tuple[1][2])