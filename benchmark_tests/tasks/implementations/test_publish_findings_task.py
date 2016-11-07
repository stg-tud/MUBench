from os.path import join
from tempfile import mkdtemp
from unittest.mock import MagicMock

from nose.tools import assert_equals

from benchmark.data.experiment import Experiment
from benchmark.data.finding import SpecializedFinding
from benchmark.data.run import Run
from benchmark.tasks.implementations.publish_findings_task import PublishFindingsTask
from benchmark.utils.io import remove_tree, create_file
from benchmark_tests.data.test_misuse import create_misuse
from benchmark_tests.test_utils.data_util import create_project, create_version
from detectors.dummy.dummy import DummyDetector


# noinspection PyAttributeOutsideInit
class TestPublishFindingsTask:
    def setup(self):
        self.dataset = "-d-"
        self.project = create_project("-p-")
        self.misuse = create_misuse("-m-", project=self.project)
        self.version = create_version("-v-", project=self.project, misuses=[self.misuse])

        self.detector = DummyDetector("-detectors-path-")
        self.experiment = Experiment(Experiment.PROVIDED_PATTERNS, self.detector, "-findings-path-", "-reviews-path-")
        self.test_run = Run([MagicMock()])
        self.test_run.is_success = lambda: False
        self.test_run.is_error = lambda: False
        self.test_run.is_timeout = lambda: False
        self.experiment.get_run = lambda v: self.test_run

        self.uut = PublishFindingsTask(self.experiment, self.dataset, "http://dummy.url")

        self.last_post_url = None
        self.last_post_data = None
        self.last_post_files = None

        def post_mock(url, data, files):
            self.last_post_url = url
            self.last_post_data = data
            self.last_post_files = files

        self.uut.post = post_mock

    def test_upload_successful_run(self):
        self.test_run.is_success = lambda: True
        self.test_run.get_runtime = lambda: 42
        findings = [
            SpecializedFinding({"id": "-1-", "misuse": "-p-.-m1-", "detector_specific": "-specific1-"}),
            SpecializedFinding({"id": "-2-", "misuse": "-p-.-m2-", "detector_specific": "-specific2-"})
        ]
        self.test_run.get_findings = lambda: findings
        potential_hits = findings[:1]
        self.test_run.get_potential_hits = lambda: potential_hits

        self.uut.process_project_version(self.project, self.version)
        self.uut.end()

        assert_equals([{
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": self.project.id,
            "version": self.version.version_id,
            "result": "success",
            "runtime": 42.0,
            "number_of_findings": 2,
            "potential_hits": potential_hits
        }], self.last_post_data)

    def test_uploads_files(self):
        self.test_run.is_success = lambda: True

        self.test_run.get_potential_hits = lambda: [
            SpecializedFinding({"id": "-1-"}, files=["-file1-"]),
            SpecializedFinding({"id": "-2-"}, files=["-file2-"])
        ]

        self.uut.process_project_version(self.project, self.version)
        self.uut.end()

        assert_equals(self.last_post_files, ["-file1-", "-file2-"])

    def test_upload_error_run(self):
        self.test_run.is_error = lambda: True
        self.test_run.get_runtime = lambda: 1337

        self.uut.process_project_version(self.project, self.version)
        self.uut.end()

        assert_equals([{
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": self.project.id,
            "version": self.version.version_id,
            "result": "error",
            "runtime": 1337,
            "number_of_findings": 0,
            "potential_hits": []
        }], self.last_post_data)

    def test_upload_timeout_run(self):
        self.test_run.is_timeout = lambda: True
        self.test_run.get_runtime = lambda: 1000000

        self.uut.process_project_version(self.project, self.version)
        self.uut.end()

        assert_equals([{
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": self.project.id,
            "version": self.version.version_id,
            "result": "timeout",
            "runtime": 1000000,
            "number_of_findings": 0,
            "potential_hits": []
        }], self.last_post_data)

    def test_upload_not_run(self):
        self.test_run.get_runtime = lambda: 0

        self.uut.process_project_version(self.project, self.version)
        self.uut.end()

        assert_equals([{
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": self.project.id,
            "version": self.version.version_id,
            "result": "not run",
            "runtime": 0,
            "number_of_findings": 0,
            "potential_hits": []
        }], self.last_post_data)

    def test_nothing_to_upload(self):
        self.uut.end()

        assert_equals(self.last_post_url, None)  # == post was not invoked

    def test_post_url(self):
        self.uut.process_project_version(self.project, self.version)
        self.uut.end()

        assert_equals(self.last_post_url, "http://dummy.url/upload/ex1")


class TestRequestFileTuple:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-test-request_file_tuple_")
        self.file = join(self.temp_dir, "file.png")
        create_file(self.file)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_create_request_file_tuple_name(self):
        actual_tuple = PublishFindingsTask._get_request_file_tuple(self.file)

        assert_equals("file.png", actual_tuple[0])
        assert_equals("file.png", actual_tuple[1][0])

    def test_create_request_file_tuple_stream(self):
        actual_tuple = PublishFindingsTask._get_request_file_tuple(self.file)

        assert_equals(self.file, actual_tuple[1][1].name)
        assert_equals('rb', actual_tuple[1][1].mode)

    def test_create_request_file_tuple_mime_type(self):
        actual_tuple = PublishFindingsTask._get_request_file_tuple(self.file)

        assert_equals('image/png', actual_tuple[1][2])