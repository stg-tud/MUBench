import logging
from os.path import join
from tempfile import mkdtemp
from unittest import mock
from unittest.mock import MagicMock, PropertyMock, patch

from nose.tools import assert_equals

from data.detector_execution import DetectOnlyExecution, MineAndDetectExecution, Result, DetectorExecution, DetectorMode
from data.findings_filters import PotentialHits, AllFindings
from data.project_compile import ProjectCompile
from tests.data.stub_detector import StubDetector
from utils.io import remove_tree, write_yaml
from utils.shell import Shell, CommandFailedError
from tests.test_utils.data_util import create_misuse, create_version, create_project


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
        self.temp_dir = mkdtemp(prefix='mubench-run-test_')
        self.findings_path = join(self.temp_dir, "-findings-")

        self.detector = StubDetector()
        self.version = create_version("-v-")
        self.findings_base_path = "-findings-"

        self.uut = DetectorExecutionTestImpl(DetectorMode.detect_only, self.detector, self.version,
                                             self.findings_base_path, AllFindings(self.detector))

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_run_outdated(self):
        with mock.patch('tests.data.stub_detector.StubDetector.md5', new_callable=PropertyMock) as mock_md5:
            mock_md5.return_value = "-md5-"
            detector = StubDetector()

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

    def test_load(self):
        self.write_run_file({"result": "success", "runtime": "23.42", "message": "-arbitrary text-"})

        execution = MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings(self.detector))

        assert execution.is_success()
        assert_equals(execution.runtime, "23.42")
        assert_equals(execution.message, "-arbitrary text-")

    def write_run_file(self, run_data):
        write_yaml(run_data, join(self.findings_path,
                                  DetectorMode.mine_and_detect.name, self.detector.id,
                                  self.version.project_id, self.version.version_id, DetectorExecution.RUN_FILE))


class TestDetectorExecution:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version = create_version("-version-", project=create_project("-project-"))
        self.detector = StubDetector()
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

    def test_execute_captures_error_output(self):
        Shell.exec = MagicMock(side_effect=CommandFailedError("-cmd-", "-out-"))

        self.uut.execute("-compiles-", 42, self.logger)

        assert_equals("Failed to execute '-cmd-': -out-", self.uut.message)

    def test_execute_cuts_output_if_too_long(self):
        long_output = "\n".join(["line " + str(i) for i in range(1, 8000)])
        Shell.exec = MagicMock(side_effect=CommandFailedError("-cmd-", long_output))

        self.uut.execute("-compiles-", 42, self.logger)

        print(self.uut.message)
        assert_equals(5000, len(str.splitlines(self.uut.message)))

    def test_execute_sets_timeout(self):
        Shell.exec = MagicMock(side_effect=TimeoutError())

        self.uut.execute("-compiles-", 42, self.logger)

        assert_equals(Result.timeout, self.uut.result)

    def test_saves_after_execution(self):
        self.uut.execute("-compiles-", 42, self.logger)

        self.uut.save.assert_called_with()


@patch("data.detector_execution.Shell")
@patch("data.project_compile.ProjectCompile.get_dependency_classpath")
class TestDetectOnlyExecution:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('-misuse-', meta={"location": {"file": "a", "method": "m()"}})
        self.version = create_version("-version-", misuses=[self.misuse], project=create_project("-project-"))
        self.detector = StubDetector()
        self.findings_base_path = "-findings-"

        self.logger = logging.getLogger("test")

        self.uut = DetectOnlyExecution(self.detector, self.version, self.misuse, self.findings_base_path,
                                       PotentialHits(self.detector, self.misuse))
        self.uut.save = MagicMock()

    def test_execute_per_misuse(self, get_dependencies_classpath_mock, shell_mock):
        jar = self.detector.jar_path
        findings_path = join("-findings-", "detect_only", "StubDetector", "-project-", "-version-", "-misuse-")
        target = join(findings_path, "findings.yml")
        run_info = join(findings_path, "run.yml")
        compiles_path = join("-compiles-", "-project-", "-version-")
        training_src_path = join(compiles_path, "patterns-src", "-misuse-")
        training_classpath = join(compiles_path, "patterns-classes", "-misuse-")
        target_src_path = join(compiles_path, "misuse-src")
        target_classpath = join(compiles_path, "misuse-classes")
        original_classpath = join(compiles_path, "original-classes.jar")
        dependencies_classpath = "-dependencies-classpath-"
        get_dependencies_classpath_mock.return_value = dependencies_classpath

        self.uut.execute("-compiles-", 42, self.logger)

        shell_mock.exec.assert_called_with('java -jar "{}" '.format(jar) +
                                           'target "{}" '.format(target) +
                                           'run_info "{}" '.format(run_info) +
                                           'detector_mode "1" ' +
                                           'training_src_path "{}" '.format(training_src_path) +
                                           'training_classpath "{}" '.format(training_classpath) +
                                           'target_src_path "{}" '.format(target_src_path) +
                                           'target_classpath "{}" '.format(target_classpath) +
                                           'dep_classpath "{}"'.format(original_classpath + ":" + dependencies_classpath),
                                           logger=self.logger,
                                           timeout=42)


@patch("data.detector_execution.Shell")
@patch("data.project_compile.ProjectCompile.get_dependency_classpath")
class TestMineAndDetectExecution:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version = create_version("-version-", project=create_project("-project-"))
        self.detector = StubDetector()
        self.findings_base_path = "-findings-"

        self.logger = logging.getLogger("test")

        self.uut = MineAndDetectExecution(self.detector, self.version, self.findings_base_path,
                                          AllFindings(self.detector))
        self.uut.save = MagicMock

    def test_execute(self, get_dependencies_classpath_mock, shell_mock):
        jar = self.detector.jar_path
        findings_path = join("-findings-", "mine_and_detect", "StubDetector", "-project-", "-version-")
        target = join(findings_path, "findings.yml")
        run_info = join(findings_path, "run.yml")
        compiles_path = join("-compiles-", "-project-", "-version-")
        target_src_path = join(compiles_path, "original-src")
        target_classpath = join(compiles_path, "original-classes")
        dependencies_classpath = "-dependencies-classpath-"
        get_dependencies_classpath_mock.return_value = dependencies_classpath

        self.uut.execute("-compiles-", 42, self.logger)

        shell_mock.exec.assert_called_with('java -jar "{}" '.format(jar) +
                                           'target "{}" '.format(target) +
                                           'run_info "{}" '.format(run_info) +
                                           'detector_mode "0" ' +
                                           'target_src_path "{}" '.format(target_src_path) +
                                           'target_classpath "{}" '.format(target_classpath) +
                                           'dep_classpath "{}"'.format(dependencies_classpath),
                                           logger=self.logger,
                                           timeout=42)
