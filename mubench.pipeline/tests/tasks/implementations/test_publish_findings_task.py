from typing import Dict
from unittest.mock import MagicMock, patch

from nose.tools import assert_equals

from data.detector import Detector
from data.detector_run import DetectorRun
from data.finding import Finding
from data.snippets import Snippet
from tasks.implementations.findings_filters import PotentialHits
from tasks.implementations.publish_findings import PublishFindingsTask
from tests.data.stub_detector import StubDetector
from tests.data.test_misuse import create_misuse
from tests.test_utils.data_util import create_project, create_version


# noinspection PyAttributeOutsideInit
@patch("tasks.implementations.publish_findings.PublishFindingsTask._PublishFindingsTask__get_potential_hit_size", return_value=0)
@patch("tasks.implementations.publish_findings.post")
class TestPublishFindingsTask:
    def setup(self):
        self.project = create_project("-p-")
        self.misuse = create_misuse("-m-", project=self.project)
        self.version = create_version("-v-", project=self.project, misuses=[self.misuse],
                                      meta={"build": {"src": "", "classes": ""}})
        self.version_compile = self.version.get_compile("/sources")

        self.test_detector_execution = MagicMock()  # type: DetectorRun
        self.test_detector_execution.is_success = lambda: False
        self.test_detector_execution.is_error = lambda: False
        self.test_detector_execution.is_timeout = lambda: False
        self.test_detector_execution.runtime = 0
        self.test_detector_execution.number_of_findings = 0
        self.test_run_timestamp = 1337
        self.test_detector_execution.get_run_info = lambda: {
            'number_of_findings': self.test_detector_execution.number_of_findings,
            'runtime': self.test_detector_execution.runtime,
            'timestamp': self.test_run_timestamp
        }
        self.test_detector_execution.findings_path = "-findings-"

        self.created_files_per_finding = dict()

        self.detector = StubDetector()  # type: Detector
        self.detector.id = "test_detector"

        self.experiment_id = "ex1"

        self.test_potential_hits = PotentialHits([])

        self.uut = PublishFindingsTask(self.experiment_id, "/sources", "http://dummy.url", "-username-", "-password-")

    def test_post_url(self, post_mock, _):
        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals("http://dummy.url/experiments/{}/detectors/{}/projects/{}/versions/{}/runs".format(
            "1", self.detector.id, self.project.id, self.version.version_id), post_mock.call_args[0][0])

    @patch("tasks.implementations.publish_findings.getpass.getpass")
    def test_post_auth_prompt(self, pass_mock, post_mock, _):
        pass_mock.return_value = "-password-"

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals("-username-", post_mock.call_args[1]["username"])
        assert_equals("-password-", post_mock.call_args[1]["password"])

    @patch("tasks.implementations.publish_findings.getpass.getpass")
    def test_post_auth_provided(self, pass_mock, post_mock, _):
        pass_mock.side_effect = UserWarning("should skip prompt")
        self.uut.review_site_password = "-password-"

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals("-username-", post_mock.call_args[1]["username"])
        assert_equals("-password-", post_mock.call_args[1]["password"])

    @patch("tasks.implementations.publish_findings.PublishFindingsTask._convert_graphs_to_files")
    def test_publish_successful_run(self, convert_mock, post_mock, _):
        self.test_detector_execution.is_success = lambda: True
        self.test_detector_execution.runtime = 42
        self.test_detector_execution.number_of_findings = 5
        potential_hits = [
            self._create_finding({"rank": "-1-"}, convert_mock),
            self._create_finding({"rank": "-2-"}, convert_mock)
        ]
        self.test_potential_hits = PotentialHits(potential_hits)

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals({
            "result": "success",
            "runtime": 42.0,
            "number_of_findings": 5,
            "potential_hits": [
                {"rank": "-1-", "target_snippets": []},
                {"rank": "-2-", "target_snippets": []}
            ],
            "timestamp": self.test_run_timestamp
        }, post_mock.call_args[0][1])

    @patch("tasks.implementations.publish_findings.PublishFindingsTask._convert_graphs_to_files")
    def test_publish_successful_run_files(self, convert_mock, post_mock, _):
        self.test_detector_execution.is_success = lambda: True

        self.test_potential_hits = PotentialHits([
            self._create_finding({"rank": "-1-"}, convert_mock, file_paths=["-file1-"]),
            self._create_finding({"rank": "-2-"}, convert_mock, file_paths=["-file2-"])
        ])

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals(["-file1-", "-file2-"], post_mock.call_args[1]["file_paths"])

    @patch("tasks.implementations.publish_findings.PublishFindingsTask._convert_graphs_to_files")
    def test_publish_successful_run_in_chunks(self, convert_mock, post_mock, _):
        self.uut.max_files_per_post = 1
        self.test_detector_execution.is_success = lambda: True
        self.test_potential_hits = PotentialHits([
            self._create_finding({"rank": "-1-"}, convert_mock, file_paths=["-file1-"]),
            self._create_finding({"rank": "-2-"}, convert_mock, file_paths=["-file2-"])
        ])

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals(len(post_mock.call_args_list), 2)
        assert_equals(["-file1-"], post_mock.call_args_list[0][1]["file_paths"])
        assert_equals(["-file2-"], post_mock.call_args_list[1][1]["file_paths"])

    @patch("tasks.implementations.publish_findings.PublishFindingsTask._convert_graphs_to_files")
    def test_publish_successful_run_in_partial_chunks(self, convert_mock, post_mock, _):
        self.uut.max_files_per_post = 3
        self.test_detector_execution.is_success = lambda: True
        self.test_potential_hits = PotentialHits([
            self._create_finding({"rank": "-1-"}, convert_mock, file_paths=["-file1-", "-file2-"]),
            self._create_finding({"rank": "-2-"}, convert_mock, file_paths=["-file3-", "-file4-"])
        ])

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals(2, len(post_mock.call_args_list))

    @patch("tasks.implementations.publish_findings.PublishFindingsTask._convert_graphs_to_files")
    def test_publish_successful_run_code_snippets(self, convert_mock, post_mock, _):
        self.test_detector_execution.is_success = lambda: True
        self.test_potential_hits = PotentialHits(
            [self._create_finding({"rank": "42"}, convert_mock, snippets=[Snippet("-code-", 23)])])

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals([{"code": "-code-", "first_line_number": 23}],
                      post_mock.call_args[0][1]["potential_hits"][0]["target_snippets"])

    @patch("tasks.implementations.publish_findings.PublishFindingsTask._convert_graphs_to_files")
    def test_publish_successful_run_code_snippets_extraction_fails(self, convert_mock, post_mock, _):
        self.test_detector_execution.is_success = lambda: True
        finding = self._create_finding({"rank": "42"}, convert_mock)
        finding.get_snippets = MagicMock(return_value=[])
        self.test_potential_hits = PotentialHits([finding])

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals([], post_mock.call_args[0][1]["potential_hits"][0]["target_snippets"])

    def test_publish_erroneous_run(self, post_mock, _):
        self.test_detector_execution.number_of_findings = 0
        self.test_detector_execution.is_error = lambda: True
        self.test_detector_execution.runtime = 1337

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals({
            "result": "error",
            "runtime": 1337,
            "number_of_findings": 0,
            "potential_hits": [],
            "timestamp": self.test_run_timestamp
        }, post_mock.call_args[0][1])

    def test_publish_timeout_run(self, post_mock, _):
        self.test_detector_execution.is_timeout = lambda: True
        self.test_detector_execution.runtime = 1000000
        self.test_detector_execution.number_of_findings = 0

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals({
            "result": "timeout",
            "runtime": 1000000,
            "number_of_findings": 0,
            "potential_hits": [],
            "timestamp": self.test_run_timestamp
        }, post_mock.call_args[0][1])

    def test_publish_not_run(self, post_mock, _):
        self.test_detector_execution.runtime = 0
        self.test_detector_execution.number_of_findings = 0

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals({
            "result": "not run",
            "runtime": 0,
            "number_of_findings": 0,
            "potential_hits": [],
            "timestamp": self.test_run_timestamp
        }, post_mock.call_args[0][1])

    @patch("tasks.implementations.publish_findings.PublishFindingsTask._convert_graphs_to_files")
    def test_with_markdown(self, convert_mock, post_mock, _):
        self.test_detector_execution.is_success = lambda: True
        potential_hits = [self._create_finding({"list": ["hello", "world"], "dict": {"key": "value"}}, convert_mock)]
        self.test_potential_hits = PotentialHits(potential_hits)
        self.test_detector_execution.get_run_info = lambda: {"info": {"k1": "v1"}, "timestamp": 0}

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals("k1: \nv1", post_mock.call_args[0][1]["info"])
        assert_equals([{"list": "* hello\n* world", "dict": "key: \nvalue", "target_snippets": []}],
                      post_mock.call_args[0][1]["potential_hits"])

    @patch("tasks.implementations.publish_findings.replace_dot_graph_with_image")
    def test_converts_graphs(self, replace_mock, post_mock, _):
        self.test_detector_execution.is_success = lambda: True

        self.test_potential_hits = PotentialHits([
            self._create_finding({"graph": 'graph G {\n' +
                                           '1 [label="JButton#button#addActionListener" shape=box style=rounded]\n' +
                                           '2 [label="JButton#button#setText" shape=box style=rounded]\n' +
                                           '3 [label="ActionListener#ActionListener#new" shape=box style=rounded]\n' +
                                           '2 -> 1 [label=""];\n' +
                                           '2 -> 3 [label=""];\n' +
                                           '3 -> 1 [label=""];\n' +
                                           '}\n'})
        ])
        replace_mock.side_effect = lambda finding, key, path: path + "/" + key

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals([self.test_detector_execution.findings_path + "/graph"], post_mock.call_args[1]["file_paths"])

    @patch("tasks.implementations.publish_findings.replace_dot_graph_with_image")
    def test_converts_directed_graphs(self, replace_mock, post_mock, _):
        self.test_detector_execution.is_success = lambda: True

        self.test_potential_hits = PotentialHits([
            self._create_finding({"graph": 'digraph G {\n' +
                                           '1 [label="JButton#button#addActionListener" shape=box style=rounded]\n' +
                                           '2 [label="JButton#button#setText" shape=box style=rounded]\n' +
                                           '3 [label="ActionListener#ActionListener#new" shape=box style=rounded]\n' +
                                           '2 -> 1 [label=""];\n' +
                                           '2 -> 3 [label=""];\n' +
                                           '3 -> 1 [label=""];\n' +
                                           '}\n'})
        ])
        replace_mock.side_effect = lambda finding, key, path: path + "/" + key

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals([self.test_detector_execution.findings_path + "/graph"], post_mock.call_args[1]["file_paths"])

    @patch("tasks.implementations.publish_findings.PublishFindingsTask._convert_graphs_to_files")
    def test_publish_successful_run_in_sized_chunks(self, convert_mock, post_mock, get_potential_hit_size_mock):
        self.uut.max_files_per_post = 100
        self.uut.max_file_size_per_post = 1500
        get_potential_hit_size_mock.return_value = 1024
        self.test_detector_execution.is_success = lambda: True
        self.test_potential_hits = PotentialHits([
            self._create_finding({"rank": "-1-"}, convert_mock, file_paths=["-file1-"]),
            self._create_finding({"rank": "-2-"}, convert_mock, file_paths=["-file2-"])
        ])

        self.uut.run(self.project, self.version, self.test_detector_execution, self.test_potential_hits,
                     self.version_compile, self.detector)

        assert_equals(len(post_mock.call_args_list), 2)
        assert_equals(["-file1-"], post_mock.call_args_list[0][1]["file_paths"])
        assert_equals(["-file2-"], post_mock.call_args_list[1][1]["file_paths"])

    def _create_finding(self, data: Dict, convert_mock=None, file_paths=None, snippets=None):
        if snippets is None:
            snippets = []
        if file_paths is None:
            file_paths = []

        finding = Finding(data)
        finding.get_snippets = lambda source_paths: \
            snippets if source_paths == ["/sources/-p-/-v-/build/"] else {}["illegal source paths: %s" % source_paths]

        if convert_mock is not None:
            self.created_files_per_finding[str(finding)] = file_paths
            convert_mock.side_effect = lambda f, p: self.created_files_per_finding[str(f)]

        return finding
