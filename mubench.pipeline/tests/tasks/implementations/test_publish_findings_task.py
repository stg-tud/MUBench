from typing import Dict
from unittest.mock import MagicMock, patch

from nose.tools import assert_equals

from data.detector import Detector
from data.experiment import Experiment
from data.finding import SpecializedFinding
from data.snippets import Snippet
from data.run import Run
from tasks.implementations.publish_findings_task import PublishFindingsTask
from tests.data.test_misuse import create_misuse
from tests.test_utils.data_util import create_project, create_version


@patch("tasks.implementations.publish_findings_task.post")
class TestPublishFindingsTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.dataset = "-d-"
        self.project = create_project("-p-")
        self.misuse = create_misuse("-m-", project=self.project)
        self.version = create_version("-v-", project=self.project, misuses=[self.misuse])

        self.test_run = Run([MagicMock()])
        self.test_run.is_success = lambda: False
        self.test_run.is_error = lambda: False
        self.test_run.is_timeout = lambda: False

        self.detector = MagicMock()  # type: Detector
        self.detector.id = "test_detector"

        self.experiment = MagicMock()  # type: Experiment
        self.experiment.id = "test_experiment"
        self.experiment.get_run = lambda v: self.test_run
        self.experiment.detector = self.detector

        self.uut = PublishFindingsTask(self.experiment, self.dataset, "/sources", "http://dummy.url", "-username-")

    def test_post_url(self, post_mock):
        self.uut.process_project_version(self.project, self.version)

        assert_equals(post_mock.call_args[0][0], "http://dummy.url/api/upload/" + self.experiment.id)

    @patch("tasks.implementations.publish_findings_task.getpass.getpass")
    def test_post_auth_prompt(self, pass_mock, post_mock):
        pass_mock.return_value = "-password-"

        self.uut.start()  # asks for password once on start
        self.uut.process_project_version(self.project, self.version)

        assert_equals(post_mock.call_args[1]["username"], "-username-")
        assert_equals(post_mock.call_args[1]["password"], "-password-")

    @patch("tasks.implementations.publish_findings_task.getpass.getpass")
    def test_post_auth_provided(self, pass_mock, post_mock):
        pass_mock.side_effect = UserWarning("should skip prompt")
        self.uut.review_site_password = "-password-"

        self.uut.start()  # should not ask for a password, since already set
        self.uut.process_project_version(self.project, self.version)

        assert_equals(post_mock.call_args[1]["username"], "-username-")
        assert_equals(post_mock.call_args[1]["password"], "-password-")

    def test_publish_successful_run(self, post_mock):
        self.test_run.is_success = lambda: True
        self.test_run.get_runtime = lambda: 42
        potential_hits = [
            _create_finding({"rank": "-1-", "misuse": "-p-.-m1-", "detector_specific": "-specific1-"}),
            _create_finding({"rank": "-2-", "misuse": "-p-.-m2-", "detector_specific": "-specific2-"})
        ]
        self.test_run.get_number_of_findings = lambda: 5
        self.test_run.get_potential_hits = lambda: potential_hits

        self.uut.process_project_version(self.project, self.version)

        assert_equals(post_mock.call_args[0][1], {
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": self.project.id,
            "version": self.version.version_id,
            "result": "success",
            "runtime": 42.0,
            "number_of_findings": 5,
            "potential_hits": potential_hits
        })

    def test_publish_successful_run_files(self, post_mock):
        self.test_run.is_success = lambda: True

        self.test_run.get_potential_hits = lambda: [
            _create_finding({"rank": "-1-"}, file_paths=["-file1-"]),
            _create_finding({"rank": "-2-"}, file_paths=["-file2-"])
        ]

        self.uut.process_project_version(self.project, self.version)

        assert_equals(post_mock.call_args[1]["file_paths"], ["-file1-", "-file2-"])

    def test_publish_successful_run_in_chunks(self, post_mock):
        self.uut.max_files_per_post = 1
        self.test_run.is_success = lambda: True
        self.test_run.get_potential_hits = lambda: [
            _create_finding({"rank": "-1-"}, file_paths=["-file1-"]),
            _create_finding({"rank": "-2-"}, file_paths=["-file2-"])
        ]

        self.uut.process_project_version(self.project, self.version)

        assert_equals(len(post_mock.call_args_list), 2)
        assert_equals(post_mock.call_args_list[0][1]["file_paths"], ["-file1-"])
        assert_equals(post_mock.call_args_list[1][1]["file_paths"], ["-file2-"])

    def test_publish_successful_run_in_partial_chunks(self, post_mock):
        self.uut.max_files_per_post = 3
        self.test_run.is_success = lambda: True
        self.test_run.get_potential_hits = lambda: [
            _create_finding({"rank": "-1-"}, file_paths=["-file1-", "-file2-"]),
            _create_finding({"rank": "-2-"}, file_paths=["-file3-", "-file4-"])
        ]

        self.uut.process_project_version(self.project, self.version)

        assert_equals(len(post_mock.call_args_list), 2)

    def test_publish_successful_run_code_snippets(self, post_mock):
        self.test_run.is_success = lambda: True
        self.test_run.get_potential_hits = lambda: [_create_finding({"rank": "42"}, snippets=[Snippet("-code-", 23)])]

        self.uut.process_project_version(self.project, self.version)

        assert_equals(post_mock.call_args[0][1]["potential_hits"][0]["target_snippets"],
                      [{"code": "-code-", "first_line_number": 23}])

    def test_publish_erroneous_run(self, post_mock):
        self.test_run.is_error = lambda: True
        self.test_run.get_runtime = lambda: 1337

        self.uut.process_project_version(self.project, self.version)

        assert_equals(post_mock.call_args[0][1], {
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": self.project.id,
            "version": self.version.version_id,
            "result": "error",
            "runtime": 1337,
            "number_of_findings": 0,
            "potential_hits": []
        })

    def test_publish_timeout_run(self, post_mock):
        self.test_run.is_timeout = lambda: True
        self.test_run.get_runtime = lambda: 1000000

        self.uut.process_project_version(self.project, self.version)

        assert_equals(post_mock.call_args[0][1], {
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": self.project.id,
            "version": self.version.version_id,
            "result": "timeout",
            "runtime": 1000000,
            "number_of_findings": 0,
            "potential_hits": []
        })

    def test_publish_not_run(self, post_mock):
        self.test_run.get_runtime = lambda: 0

        self.uut.process_project_version(self.project, self.version)

        assert_equals(post_mock.call_args[0][1], {
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": self.project.id,
            "version": self.version.version_id,
            "result": "not run",
            "runtime": 0,
            "number_of_findings": 0,
            "potential_hits": []
        })

    def test_nothing_to_upload(self, post_mock):
        self.uut.end()

        post_mock.assert_not_called()


def _create_finding(data: Dict, file_paths=None, snippets=None):
    if snippets is None:
        snippets = []
    if file_paths is None:
        file_paths = []
    finding = SpecializedFinding(data, files=file_paths)
    finding.get_snippets = lambda source_path:\
        snippets if source_path == "/sources/-p-/-v-/original-src" else {}["illegal source path: %s" % source_path]
    return finding
