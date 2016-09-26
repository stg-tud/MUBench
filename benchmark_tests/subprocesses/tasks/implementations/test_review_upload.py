import json
from os.path import join
from tempfile import mkdtemp
from typing import Dict, List

from nose.tools import assert_equals

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark.subprocesses.tasks.implementations.detect import Run, Result
from benchmark.subprocesses.tasks.implementations.review_upload import ReviewUpload, Request
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

        self.detector = Detector(join(self.temp_dir, "detectors"), TEST_DETECTOR_ID)
        self.experiment = Experiment(Experiment.PROVIDED_PATTERNS, self.detector, self.findings_path,
                                     join(self.temp_dir, "reviews"))
        self.test_run = self.experiment.get_run(self.version)
        self.test_run.result = Result.success
        self.experiment.get_run = lambda v: self.test_run

        self.uut = ReviewUpload(self.experiment, self.dataset, self.detector, self.checkout_base_dir)

        self.potential_hits = []
        self.uut.find_potential_hits = lambda f, m: self.potential_hits

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
        assert_equals(actual_url, ReviewUpload.URL_EX1)

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

        self.detector = Detector(join(self.temp_dir, "detectors"), TEST_DETECTOR_ID)
        self.experiment = Experiment(Experiment.TOP_FINDINGS, self.detector, self.findings_path,
                                     join(self.temp_dir, "reviews"))
        self.test_run = self.experiment.get_run(self.version)
        self.test_run.result = Result.success
        self.experiment.get_run = lambda v: self.test_run

        self.uut = ReviewUpload(self.experiment, self.dataset, self.detector, self.checkout_base_dir)

        self.potential_hits = []
        self.uut.find_potential_hits = lambda f, m: self.potential_hits

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
        assert_equals(actual_url, ReviewUpload.URL_EX2)

    def test_request_contains_findings(self):
        self.uut.request_data = [Request(TEST_DATASET, self.detector, self.project, self.version,
                                         [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific1-"},
                                          {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific2-"}])]

        self.uut.end()

        actual_url = self.post_url
        assert_equals(actual_url, ReviewUpload.URL_EX2)


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

        self.detector = Detector(join(self.temp_dir, "detectors"), TEST_DETECTOR_ID)
        self.experiment = Experiment(Experiment.BENCHMARK, self.detector, self.findings_path,
                                     join(self.temp_dir, "reviews"))
        self.test_run = self.experiment.get_run(self.version)
        self.test_run.result = Result.success
        self.experiment.get_run = lambda v: self.test_run

        self.uut = ReviewUpload(self.experiment, self.dataset, self.detector, self.checkout_base_dir)

        self.potential_hits = []
        self.uut.find_potential_hits = lambda f, m: self.potential_hits

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
        self.potential_hits = [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific2-"},
                               {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific1-"}]

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        actual = self.uut.request_data[0]
        assert_equals(self.potential_hits, actual.findings)

    def test_post_url(self):
        self.uut.request_data = [Request(TEST_DATASET, self.detector, self.project, self.version,
                                         [{"id": "-1-", "misuse": "-p-.-m1-", "detector-specific": "-specific1-"},
                                          {"id": "-2-", "misuse": "-p-.-m2-", "detector-specific": "-specific2-"}])]

        self.uut.end()

        actual_url = self.post_url
        assert_equals(actual_url, ReviewUpload.URL_EX3)

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


class TestFindPotentialMatches:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('misuse', meta={"location": {"file": "a", "method": "m()"}})

    def test_matches_on_file(self):
        self.misuse.location.file = "some-class.java"
        self.assert_potential_hit([{"file": "some-class.java"}])

    def test_matches_on_file_absolute(self):
        self.misuse.location.file = "java/main/some-class.java"
        self.assert_potential_hit([{"file": "/some/prefix/java/main/some-class.java"}])

    def test_matches_on_class(self):
        self.misuse.location.file = "some-class.java"
        self.assert_potential_hit([{"file": "some-class.class"}])

    def test_matches_on_inner_class(self):
        self.misuse.location.file = "some-class.java"
        self.assert_potential_hit([{"file": "some-class$inner-class.class"}])

    def test_differs_on_method(self):
        self.misuse.location.method = "method()"
        self.assert_no_potential_hit([{"method": "other_method()"}])

    def test_matches_on_method_name(self):
        self.misuse.location.method = "method(A, B)"
        self.assert_potential_hit([{"method": "method"}])

    def test_differs_on_method_name_prefix(self):
        self.misuse.location.method = "appendX"
        self.assert_no_potential_hit([{"method": "append"}])

    def test_matches_on_method_signature(self):
        self.misuse.location.method = "method(A, B)"
        self.assert_potential_hit([{"method": "method(A, B)"}])

    def test_falls_back_to_method_name_if_no_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(p.A)"}])

    def test_matches_only_on_signature_if_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(A)"}, {"method": "method(B)"}])

    def test_matches_constructor(self):
        self.misuse.location.method = "A()"
        self.assert_potential_hit([{"method": "<init>()"}])

    def create_findings(self, findings: List[Dict[str, str]]):
        for finding in findings:
            if "file" not in finding:
                finding["file"] = self.misuse.location.file
            if "method" not in finding:
                finding["method"] = self.misuse.location.method
        return findings

    def assert_potential_hit(self, findings):
        assert ReviewUpload.find_potential_hits(self.create_findings(findings), self.misuse)

    def assert_no_potential_hit(self, findings):
        assert not ReviewUpload.find_potential_hits(self.create_findings(findings), self.misuse)
