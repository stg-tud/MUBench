import logging
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp
from unittest.mock import MagicMock

from nose.tools import assert_equals

from benchmark.data.detector_execution import MineAndDetectExecution, DetectorMode, DetectorExecution
from benchmark.data.findings_filters import AllFindings
from benchmark.data.run import Run
from benchmark.utils.io import write_yaml
from benchmark.utils.shell import Shell
from benchmark_tests.test_utils.data_util import create_misuse, create_version, create_project
from detectors.dummy.dummy import DummyDetector


class TestRun:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('-misuse-', meta={"location": {"file": "a", "method": "m()"}})
        self.version = create_version("-version-", misuses=[self.misuse], project=create_project("-project-"))
        self.detector = DummyDetector("-detectors-")

        self.temp_dir = mkdtemp(prefix='mubench-run-test_')
        self.findings_path = join(self.temp_dir, "-findings-")

        self.logger = logging.getLogger("test")

        self.__orig_shell_exec = Shell.exec
        Shell.exec = MagicMock()

    def teardown(self):
        rmtree(self.temp_dir)
        Shell.exec = self.__orig_shell_exec

    def test_not_run(self):
        run = Run([])
        assert not run.is_success()
        assert not run.is_failure()

    def test_error(self):
        self.write_run_file({"result": "error"})

        run = Run([MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings(self.detector))])

        assert run.is_error()

    def test_timeout(self):
        self.write_run_file({"result": "timeout"})

        run = Run([MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings(self.detector))])

        assert run.is_timeout()

    def test_success(self):
        self.write_run_file({"result": "success"})

        run = Run([MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings(self.detector))])

        assert run.is_success()

    def test_metadata(self):
        self.write_run_file({"result": "success", "runtime": "23.42", "message": "-arbitrary text-"})

        execution = MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings(self.detector))

        assert execution.state.is_success()
        assert_equals(execution.state.runtime, "23.42")
        assert_equals(execution.state.message, "-arbitrary text-")

    def write_run_file(self, run_data):
        write_yaml(run_data, join(self.findings_path,
                                  DetectorMode.mine_and_detect.name, self.detector.id,
                                  self.version.project_id, self.version.version_id, DetectorExecution.RUN_FILE))
