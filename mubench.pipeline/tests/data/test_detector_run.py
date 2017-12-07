import logging
from os.path import join
from tempfile import mkdtemp
from unittest.mock import MagicMock, patch, ANY

from nose.tools import assert_equals

from data.detector_run import DetectorRun, Result
from data.finding import Finding
from tasks.configurations.detector_interface_configuration import key_findings_file, key_run_file
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_version, create_project
from utils.io import remove_tree
from utils.shell import CommandFailedError


@patch("data.detector_run.read_yaml_if_exists")
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

        self.uut = DetectorRun(self.detector, self.version, self.findings_path)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_run_outdated(self, read_run_info):
        self.detector.md5 = "-md5-"
        read_run_info.return_value = {"md5": "-old-md5-"}

        uut = DetectorRun(self.detector, self.version, self.findings_path)

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

        uut = DetectorRun(self.detector, self.version, self.findings_path)

        assert uut.is_success()
        assert_equals(uut.runtime, "23.42")
        assert_equals(uut.message, "-arbitrary text-")


# noinspection PyUnusedLocal
# patch prevent write to filesystem
@patch("data.detector_run.write_yaml")
class TestDetectorRun:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version = create_version("-version-", project=create_project("-project-"))
        self.detector = StubDetector()
        self.findings_path = "-findings-"
        self.findings_file_path = join(self.findings_path, "FINDINGS_FILE")
        self.run_file_path = join(self.findings_path, "run.yml")

        self.detector_args = {}

        self.logger = logging.getLogger("test")

        self.uut = DetectorRun(self.detector, self.version, self.findings_path)

    def test_execute_sets_success(self, write_yaml_mock):
        self.uut._execute("-compiles-", 42, self.logger)

        assert_equals(Result.success, self.uut.result)

    def test_execute_sets_error(self, write_yaml_mock):
        self.detector.runner_interface.execute = MagicMock(side_effect=CommandFailedError("-cmd-", "-out-"))

        self.uut._execute("-compiles-", 42, self.logger)

        assert_equals(Result.error, self.uut.result)

    def test_execute_captures_error_output(self, write_yaml_mock):
        self.detector.runner_interface.execute = MagicMock(side_effect=CommandFailedError("-cmd-", "-out-"))

        self.uut._execute("-compiles-", 42, self.logger)

        assert_equals("Failed to execute '-cmd-': -out-", self.uut.message)

    def test_execute_cuts_output_if_too_long(self, write_yaml_mock):
        long_output = "\n".join(["line " + str(i) for i in range(1, 8000)])
        self.detector.runner_interface.execute = MagicMock(side_effect=CommandFailedError("-cmd-", long_output))

        self.uut._execute("-compiles-", 42, self.logger)

        print(self.uut.message)
        assert_equals(5000, len(str.splitlines(self.uut.message)))

    def test_execute_sets_timeout(self, write_yaml_mock):
        self.detector.runner_interface.execute = MagicMock(side_effect=TimeoutError())

        self.uut._execute("-compiles-", 42, self.logger)

        assert_equals(Result.timeout, self.uut.result)

    def test_saves_after_execution(self, write_yaml_mock):
        self.uut._execute("-compiles-", 42, self.logger)

        write_yaml_mock.assert_called_with(
            {'result': 'success', 'message': '', 'md5': self.detector.md5, 'runtime': ANY},
            file='-findings-/run.yml'
        )

    def test_skips_execution_if_previous_run_succeeded(self, _):
        uut = DetectorRun(self.detector, self.version, self.findings_path)
        uut._execute = MagicMock()

        uut.is_outdated = lambda: False
        uut.is_error = lambda: False
        uut.is_success = lambda: True

        uut.ensure_executed(self.detector_args, None, False, self.logger)

        uut._execute.assert_not_called()

    def test_skips_detect_if_previous_run_was_error(self, _):
        uut = DetectorRun(self.detector, self.version, self.findings_path)
        uut._execute = MagicMock()

        uut.is_outdated = lambda: False
        uut.is_error = lambda: True

        uut.ensure_executed(self.detector_args, None, False, self.logger)

        uut._execute.assert_not_called()

    def test_force_detect_on_new_detector(self, _):
        uut = DetectorRun(self.detector, self.version, self.findings_path)
        uut._execute = MagicMock()

        uut.is_success = lambda: True
        uut.is_outdated = lambda: True

        uut.ensure_executed(self.detector_args, None, False, self.logger)

        uut._execute.assert_called_with(ANY, None, ANY)

    def test_adds_run_file_path_arg(self, _):
        uut = DetectorRun(self.detector, self.version, self.findings_path)
        uut._execute = MagicMock()

        uut.ensure_executed(self.detector_args, None, True, self.logger)

        args = uut._execute.call_args[0][0]
        assert key_run_file in args

    def test_adds_findings_file_path_arg(self, _):
        uut = DetectorRun(self.detector, self.version, self.findings_path)
        uut._execute = MagicMock()

        uut.ensure_executed(self.detector_args, None, True, self.logger)

        args = uut._execute.call_args[0][0]
        assert key_findings_file in args

    @patch("data.detector_run.open_yamls_if_exists")
    def test_adds_rank(self, read_yamls_mock, _):
        read_yamls_mock.return_value.__enter__.return_value = [{"name": "f1"}, {"name": "f2"}]
        execution = DetectorRun(StubDetector(), create_version("-v-"), "-findings-path-")

        findings = execution._load_findings()

        assert_equals(findings, [
            Finding({"name": "f1", "rank": 0}),
            Finding({"name": "f2", "rank": 1})
        ])
