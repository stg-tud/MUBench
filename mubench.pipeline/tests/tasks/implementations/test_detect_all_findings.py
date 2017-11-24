import os
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp
from unittest.mock import ANY, patch, MagicMock

from nose.tools import assert_equals, assert_raises

from data.version_compile import VersionCompile
from tasks.configurations.detector_interface_configuration import key_target_classpath, key_dependency_classpath, \
    key_detector_mode, key_target_src_path, key_findings_file, key_run_file
from tasks.implementations.detect_all_findings import DetectAllFindingsTask
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_project, create_version


# noinspection PyAttributeOutsideInit
@patch("tasks.implementations.detect_all_findings.DetectAllFindingsTask._get_run")
class TestDetectAllFindingsTask:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.compiles_path = join(self.temp_dir, "checkout")
        self.findings_base_path = join(self.temp_dir, "findings")

        os.chdir(self.temp_dir)

        self.project = create_project("-project-")
        self.version = create_version("-version-", project=self.project)
        self.detector = StubDetector()

        self.version_compile = VersionCompile(self.compiles_path, self.version.misuses)

        self.last_invoke = None

        # mock command-line invocation
        def mock_invoke_detector(detect, absolute_misuse_detector_path: str, detector_args: str):
            self.last_invoke = absolute_misuse_detector_path, detector_args

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_invokes_with_detector_args(self, get_run_mock):
        execution_mock = MagicMock()
        get_run_mock.return_value = execution_mock
        uut = DetectAllFindingsTask(self.findings_base_path, False, None, None)

        try:
            uut.run(self.detector, self.version, self.version_compile)
        except UserWarning:
            pass

        expected_args = {
            key_target_src_path: self.version_compile.original_sources_path,
            key_target_classpath: self.version_compile.original_classes_path,
            key_dependency_classpath: self.version_compile.get_full_classpath(),
            key_detector_mode: 0,
            key_findings_file: join(self.findings_base_path, "mine_and_detect", "StubDetector", "-project", "-version-",
                                    "findings.yml"),
            key_run_file: join(self.findings_base_path, "mine_and_detect", "StubDetector", "-project", "-version-",
                               "run.yml"),
        }

        execution_mock.execute.assert_called_with(ANY, None, ANY)
        actual_args = execution_mock.execute.call_args[0][0]
        assert_equals(set(expected_args), set(actual_args))

    def test_continues_without_detect_if_previous_run_succeeded(self, get_run_mock):
        execution_mock = MagicMock()
        get_run_mock.return_value = execution_mock
        uut = DetectAllFindingsTask(self.findings_base_path, False, None, None)

        execution_mock.is_outdated = lambda: False
        execution_mock.is_error = lambda: False
        execution_mock.is_success = lambda: True

        response = uut.run(self.detector, self.version, self.version_compile)

        execution_mock.execute.assert_not_called()
        assert_equals(execution_mock, response)

    def test_skips_detect_if_previous_run_was_error(self, get_run_mock):
        execution_mock = MagicMock()
        get_run_mock.return_value = execution_mock
        uut = DetectAllFindingsTask(self.findings_base_path, False, None, None)

        execution_mock.is_outdated = lambda: False
        execution_mock.is_error = lambda: True

        assert_raises(UserWarning, uut.run, self.detector, self.version, self.version_compile)

        execution_mock.execute.assert_not_called()

    def test_force_detect_on_new_detector(self, get_run_mock):
        execution_mock = MagicMock()
        get_run_mock.return_value = execution_mock
        uut = DetectAllFindingsTask(self.findings_base_path, False, None, None)

        execution_mock.is_success = lambda: True
        execution_mock.is_outdated = lambda: True

        response = uut.run(self.detector, self.version, self.version_compile)

        execution_mock.execute.assert_called_with(ANY, None, ANY)
        assert_equals(execution_mock, response)
