import logging
from os.path import join
from unittest import mock
from unittest.mock import MagicMock, PropertyMock

from nose.tools import assert_equals

from benchmark.data.detector_execution import DetectOnlyExecution, MineAndDetectExecution, Result, DetectorExecution, \
    DetectorMode
from benchmark.data.findings_filters import PotentialHits, AllFindings
from benchmark.data.project_compile import ProjectCompile
from benchmark.utils.shell import Shell, CommandFailedError
from benchmark_tests.test_utils.data_util import create_misuse, create_version, create_project
from detectors.dummy.dummy import DummyDetector


class DetectorExecutionTestImpl(DetectorExecution):
    def _get_findings_path(self):
        return "-findings-"

    def _load_findings(self):
        pass

    def _get_detector_arguments(self, project_compile: ProjectCompile):
        return []


class TestExecutionState:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = DummyDetector("-detectors-")
        self.version = create_version("-v-")
        self.findings_base_path = "-findings-"

        self.uut = DetectorExecutionTestImpl(DetectorMode.detect_only, self.detector, self.version,
                                             self.findings_base_path, AllFindings(self.detector))

    def test_run_outdated(self):
        with mock.patch('detectors.dummy.dummy.DummyDetector.md5', new_callable=PropertyMock) as mock_md5:
            mock_md5.return_value = "-md5-"
            detector = DummyDetector("-detectors-")

            uut = DetectorExecutionTestImpl(DetectorMode.detect_only, detector, self.version, self.findings_base_path,
                                            AllFindings(detector))

            assert uut.is_outdated()

    def test_run_up_to_date(self):
        self.uut._detector_md5 = self.detector.md5

        assert not self.uut.is_outdated()

    def test_error_is_failure(self):
        self.uut.is_error = lambda: True
        self.uut.is_timeout = lambda: False

        assert self.uut.is_failure()

    def test_timeout_is_failure(self):
        self.uut.is_timeout = lambda: True
        self.uut.is_error = lambda: False

        assert self.uut.is_failure()


class TestDetectorExecution:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version = create_version("-version-", project=create_project("-project-"))
        self.detector = DummyDetector("-detectors-")
        self.findings_base_path = "-findings-"

        self.logger = logging.getLogger("test")

        self.__orig_shell_exec = Shell.exec
        Shell.exec = MagicMock()

        self.uut = DetectorExecutionTestImpl(DetectorMode.detect_only, self.detector, self.version,
                                             self.findings_base_path, AllFindings(self.detector))
        self.uut.save = MagicMock()

    def teardown(self):
        Shell.exec = self.__orig_shell_exec

    def test_execute_sets_success(self):
        self.uut.execute("-compiles-", 42, self.logger)

        assert_equals(Result.success, self.uut.result)

    def test_execute_sets_error(self):
        Shell.exec = MagicMock(side_effect=CommandFailedError("-cmd-", "-out-"))

        self.uut.execute("-compiles-", 42, self.logger)

        assert_equals(Result.error, self.uut.result)

    def test_execute_sets_timeout(self):
        Shell.exec = MagicMock(side_effect=TimeoutError())

        self.uut.execute("-compiles-", 42, self.logger)

        assert_equals(Result.timeout, self.uut.result)

    def test_saves_after_execution(self):
        self.uut.execute("-compiles-", 42, self.logger)

        self.uut.save.assert_called_with()


class TestDetectOnlyExecution:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('-misuse-', meta={"location": {"file": "a", "method": "m()"}})
        self.version = create_version("-version-", misuses=[self.misuse], project=create_project("-project-"))
        self.detector = DummyDetector("-detectors-")
        self.findings_base_path = "-findings-"

        self.logger = logging.getLogger("test")

        self.__orig_shell_exec = Shell.exec
        Shell.exec = MagicMock()

        self.uut = DetectOnlyExecution(self.detector, self.version, self.misuse, self.findings_base_path,
                                       PotentialHits(self.detector, self.misuse))
        self.uut.save = MagicMock()

    def teardown(self):
        Shell.exec = self.__orig_shell_exec

    def test_execute_per_misuse(self):
        jar = join("-detectors-", "dummy", "dummy.jar")
        target = join("-findings-", "detect_only", "dummy", "-project-", "-version-", "-misuse-", "findings.yml")
        run_info = join("-findings-", "detect_only", "dummy", "-project-", "-version-", "-misuse-", "run.yml")
        training_src_path = join("-compiles-", "-project-", "-version-", "patterns-src", "-misuse-")
        training_classpath = join("-compiles-", "-project-", "-version-", "patterns-classes", "-misuse-")
        target_src_path = join("-compiles-", "-project-", "-version-", "misuse-src")
        target_classpath = join("-compiles-", "-project-", "-version-", "misuse-classes")

        self.uut.execute("-compiles-", 42, self.logger)

        Shell.exec.assert_called_with('java -jar "{}" '.format(jar) +
                                      'target "{}" '.format(target) +
                                      'run_info "{}" '.format(run_info) +
                                      'detector_mode "1" ' +
                                      'training_src_path "{}" '.format(training_src_path) +
                                      'training_classpath "{}" '.format(training_classpath) +
                                      'target_src_path "{}" '.format(target_src_path) +
                                      'target_classpath "{}"'.format(target_classpath),
                                      logger=self.logger,
                                      timeout=42)


class TestMineAndDetectExecution:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version = create_version("-version-", project=create_project("-project-"))
        self.detector = DummyDetector("-detectors-")
        self.findings_base_path = "-findings-"

        self.logger = logging.getLogger("test")

        self.__orig_shell_exec = Shell.exec
        Shell.exec = MagicMock()

        self.uut = MineAndDetectExecution(self.detector, self.version, self.findings_base_path,
                                          AllFindings(self.detector))
        self.uut.save = MagicMock

    def teardown(self):
        Shell.exec = self.__orig_shell_exec

    def test_execute(self):
        jar = join("-detectors-", "dummy", "dummy.jar")
        target = join("-findings-", "mine_and_detect", "dummy", "-project-", "-version-", "findings.yml")
        run_info = join("-findings-", "mine_and_detect", "dummy", "-project-", "-version-", "run.yml")
        target_src_path = join("-compiles-", "-project-", "-version-", "original-src")
        target_classpath = join("-compiles-", "-project-", "-version-", "original-classes")

        self.uut.execute("-compiles-", 42, self.logger)

        Shell.exec.assert_called_with('java -jar "{}" '.format(jar) +
                                      'target "{}" '.format(target) +
                                      'run_info "{}" '.format(run_info) +
                                      'detector_mode "0" ' +
                                      'target_src_path "{}" '.format(target_src_path) +
                                      'target_classpath "{}"'.format(target_classpath),
                                      logger=self.logger,
                                      timeout=42)
