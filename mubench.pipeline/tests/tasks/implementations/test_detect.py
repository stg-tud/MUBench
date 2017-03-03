import os
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp
from unittest.mock import MagicMock, ANY

from nose.tools import assert_equals

from data.detector_execution import MineAndDetectExecution
from data.experiment import Experiment
from data.findings_filters import AllFindings
from data.run import Run
from tasks.implementations.detect import Detect
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_project, create_version


# noinspection PyAttributeOutsideInit
class TestDetect:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.compiles_path = join(self.temp_dir, "checkout")
        self.findings_path = join(self.temp_dir, "findings")

        os.chdir(self.temp_dir)

        self.project = create_project("-project-")
        self.version = create_version("-version-", project=self.project)
        self.detector = StubDetector()
        self.test_run_execution = MineAndDetectExecution(self.detector, self.version, self.findings_path,
                                                         AllFindings(self.detector))
        self.test_run = Run([self.test_run_execution])
        self.test_run.execute = MagicMock(return_value="test execution successful")
        self.experiment = Experiment(Experiment.TOP_FINDINGS, self.detector, self.findings_path)
        self.experiment.get_run = lambda v: self.test_run
        self.uut = Detect(self.compiles_path, self.experiment, None, False)

        self.last_invoke = None

        # mock command-line invocation
        def mock_invoke_detector(detect, absolute_misuse_detector_path: str, detector_args: str):
            self.last_invoke = absolute_misuse_detector_path, detector_args

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_invokes_detector(self):
        self.uut.process_project_version(self.project, self.version)

        self.test_run.execute.assert_called_with(self.compiles_path, None, ANY)

    def test_skips_detect_if_previous_run_succeeded_but_continues_with_version(self):
        self.test_run.is_success = lambda: True

        response = self.uut.process_project_version(self.project, self.version)

        self.test_run.execute.assert_not_called()
        assert_equals([], response)

    def test_skips_detect_if_previous_run_was_error(self):
        self.test_run.is_error = lambda: True

        response = self.uut.process_project_version(self.project, self.version)

        self.test_run.execute.assert_not_called()
        assert_equals([self.version.id], response)

    def test_force_detect_on_new_detector(self):
        self.test_run.is_success = lambda: True
        self.test_run.is_outdated = lambda: True

        response = self.uut.process_project_version(self.project, self.version)

        self.test_run.execute.assert_called_with(self.compiles_path, None, ANY)
        assert_equals([], response)

    def test_skips_detect_only_if_no_patterns_are_available(self):
        self.experiment.id = Experiment.PROVIDED_PATTERNS

        response = self.uut.process_project_version(self.project, self.version)

        self.test_run.execute.assert_not_called()
        assert_equals([self.version.id], response)


class TestDetectorDownload:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.compiles_path = join(self.temp_dir, "checkout")
        self.findings_path = join(self.temp_dir, "findings")

        detector = StubDetector()
        experiment = Experiment(Experiment.PROVIDED_PATTERNS, detector, self.findings_path)
        self.uut = Detect(self.compiles_path, experiment, None, False)
        self.uut._download = MagicMock(return_value=True)

    def test_downloads_detector_if_not_available(self):
        self.uut._detector_available = MagicMock(return_value=False)

        self.uut.start()

        self.uut._download.assert_called_with()
