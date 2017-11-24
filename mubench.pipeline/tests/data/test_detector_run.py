import logging
from os.path import join
from tempfile import mkdtemp
from unittest.mock import MagicMock, patch, ANY

from nose.tools import assert_equals

from data.detector_run import DetectorRun, Result
from data.finding import Finding
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_version, create_project
from utils.io import remove_tree
from utils.shell import CommandFailedError


@patch("data.detector_execution.read_yaml_if_exists")
class TestExecutionState:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-run-test_')
        self.findings_path = join(self.temp_dir, "-findings-")
        self.findings_file_path = join(self.findings_path, "FINDINGS_FILE")
        self.run_file_path = join(self.findings_path, "RUN_FILE")

        self.detector = StubDetector()
        self.version = create_version("-v-")
        self.findings_base_path = "-findings-"

        self.uut = DetectorRun(self.detector, self.version, self.findings_path,
                               self.findings_file_path, self.run_file_path)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_run_outdated(self, read_run_info):
        self.detector.md5 = "-md5-"
        read_run_info.return_value = {"md5": "-old-md5-"}

        uut = DetectorRun(self.detector, self.version, self.findings_path,
                          self.findings_file_path, self.run_file_path)

        assert uut.is_outdated()

    def test_run_up_to_date(self, read_run_info):
        self.detector.md5 = "-md5-"
        read_run_info.return_value = {"md5": "-md5-"}

        assert not self.uut.is_outdated()

    def test_error_is_failure(self, read_run_info):
        read_run_info.return_value = {"result": "error"}

        assert self.uut.is_failure()

    def test_timeout_is_failure(self, read_run_info):
        read_run_info.return_value = {"result": "timeout"}

        assert self.uut.is_failure()

    def test_load(self, read_run_info):
        read_run_info.return_value = {"result": "success", "runtime": "23.42", "message": "-arbitrary text-"}

        uut = DetectorRun(self.detector, self.version, self.findings_path,
                          self.findings_file_path, self.run_file_path)

        assert uut.is_success()
        assert_equals(uut.runtime, "23.42")
        assert_equals(uut.message, "-arbitrary text-")


# noinspection PyUnusedLocal
# patch prevent write to filesystem
@patch("data.detector_execution.write_yaml")
class TestDetectorRun:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version = create_version("-version-", project=create_project("-project-"))
        self.detector = StubDetector()
        self.findings_path = "-findings-"
        self.findings_file_path = join(self.findings_path, "FINDINGS_FILE")
        self.run_file_path = join(self.findings_path, "run.yml")

        self.logger = logging.getLogger("test")

        self.uut = DetectorRun(self.detector, self.version, self.findings_path,
                               self.findings_file_path, self.run_file_path)

    def test_execute_sets_success(self, write_yaml_mock):
        self.uut.execute("-compiles-", 42, self.logger)

        assert_equals(Result.success, self.uut.result)

    def test_execute_sets_error(self, write_yaml_mock):
        self.detector.runner_interface.execute = MagicMock(side_effect=CommandFailedError("-cmd-", "-out-"))

        self.uut.execute("-compiles-", 42, self.logger)

        assert_equals(Result.error, self.uut.result)

    def test_execute_captures_error_output(self, write_yaml_mock):
        self.detector.runner_interface.execute = MagicMock(side_effect=CommandFailedError("-cmd-", "-out-"))

        self.uut.execute("-compiles-", 42, self.logger)

        assert_equals("Failed to execute '-cmd-': -out-", self.uut.message)

    def test_execute_cuts_output_if_too_long(self, write_yaml_mock):
        long_output = "\n".join(["line " + str(i) for i in range(1, 8000)])
        self.detector.runner_interface.execute = MagicMock(side_effect=CommandFailedError("-cmd-", long_output))

        self.uut.execute("-compiles-", 42, self.logger)

        print(self.uut.message)
        assert_equals(5000, len(str.splitlines(self.uut.message)))

    def test_execute_sets_timeout(self, write_yaml_mock):
        self.detector.runner_interface.execute = MagicMock(side_effect=TimeoutError())

        self.uut.execute("-compiles-", 42, self.logger)

        assert_equals(Result.timeout, self.uut.result)

    def test_saves_after_execution(self, write_yaml_mock):
        self.uut.execute("-compiles-", 42, self.logger)

        write_yaml_mock.assert_called_with(
            {'result': 'success', 'message': '', 'md5': self.detector.md5, 'runtime': ANY},
            file='-findings-/run.yml'
        )


class TestDetectorExecutionLoadFindings:
    @patch("data.detector_execution.open_yamls_if_exists")
    def test_adds_rank(self, read_yamls_mock):
        read_yamls_mock.return_value.__enter__.return_value = [{"name": "f1"}, {"name": "f2"}]
        execution = DetectorRun(StubDetector(), create_version("-v-"), "-findings-path-",
                                      "-findings-file-", "-run-file-")

        findings = execution._load_findings()

        assert_equals(findings, [
            Finding({"name": "f1", "rank": 0}),
            Finding({"name": "f2", "rank": 1})
        ])

