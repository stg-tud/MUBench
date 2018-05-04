from unittest.mock import patch, MagicMock

from nose.tools import assert_equals

from tasks.configurations.detector_interface_configuration import key_training_src_path
from tasks.implementations.crossproject_prepare import CrossProjectSourcesPaths
from tasks.implementations.detect_all_findings import DetectAllFindingsTask
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_version


@patch("tasks.implementations.detect_all_findings.DetectAllFindingsTask._get_detector_run")
class TestDetectAllFindingsTask:
    def setup(self):
        self.detector = StubDetector()
        self.version = create_version("-version-", meta={})
        self.version_compile = self.version.get_compile("-compile-")

    def test_adds_xp_training_sources(self, get_detector_run_mock):
        detector_run_mock = MagicMock()
        get_detector_run_mock.return_value = detector_run_mock
        xp_sources_paths = CrossProjectSourcesPaths(["xp_sources1", "xp_sources2"])
        uut = DetectAllFindingsTask("-findings-", False, None, -1)

        uut.run(self.detector, self.version, self.version_compile, xp_sources_paths)

        assert_equals(1, detector_run_mock.ensure_executed.call_count)
        actual_ensure_executed_args = detector_run_mock.ensure_executed.call_args[0]
        actual_detector_args = actual_ensure_executed_args[0]
        assert_equals(["xp_sources1", "xp_sources2"], actual_detector_args[key_training_src_path])
