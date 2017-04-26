import logging
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp
from unittest.mock import MagicMock

from nose.tools import assert_equals

from data.detector_execution import MineAndDetectExecution, Result
from data.findings_filters import AllFindings
from data.run import Run
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_misuse, create_version, create_project
from utils.shell import Shell


class TestRun:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('-misuse-', meta={"location": {"file": "a", "method": "m()"}})
        self.version = create_version("-version-", misuses=[self.misuse], project=create_project("-project-"))
        self.detector = StubDetector()

        self.temp_dir = mkdtemp(prefix='mubench-run-test_')
        self.findings_path = join(self.temp_dir, "-findings-")

        self.logger = logging.getLogger("test")

        self.__orig_shell_exec = Shell.exec
        Shell.exec = MagicMock()

    def teardown(self):
        rmtree(self.temp_dir)
        Shell.exec = self.__orig_shell_exec

    def test_not_run(self):
        execution = MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings(self.detector))
        run = Run([execution])
        execution.result = None

        assert not run.is_success()
        assert not run.is_failure()

    def test_error(self):
        execution = MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings(self.detector))
        run = Run([execution])
        execution.result = Result.error

        assert run.is_error()

    def test_timeout(self):
        execution = MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings(self.detector))
        run = Run([execution])
        execution.result = Result.timeout

        assert run.is_timeout()

    def test_success(self):
        execution = MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings(self.detector))
        run = Run([execution])
        execution.result = Result.success

        assert run.is_success()

    def test_get_potential_hits(self):
        execution1 = MagicMock()
        execution1.potential_hits = [{"rank": 0, "name": "finding1"}, {"rank": 1, "name": "finding2"}]
        execution2 = MagicMock()
        execution2.potential_hits = [{"rank": 0, "name": "finding3"}]
        run = Run([execution1, execution2])

        potential_hits = run.get_potential_hits()

        assert_equals(potential_hits, [
            {"rank": 0, "name": "finding1"},
            {"rank": 1, "name": "finding2"},
            {"rank": 2, "name": "finding3"}])

    def test_get_number_of_findings(self):
        execution1 = MagicMock()
        execution1.number_of_findings = 5
        execution2 = MagicMock()
        execution2.number_of_findings = 42
        run = Run([execution1, execution2])

        number_of_findings = run.get_number_of_findings()

        assert_equals(number_of_findings, 5 + 42)

    def test_get_runtime(self):
        execution1 = MagicMock()
        execution1.runtime = 10
        execution2 = MagicMock()
        execution2.runtime = 5
        run = Run([execution1, execution2])

        runtime = run.get_runtime()

        assert_equals(runtime, 7.5)

