import logging
from os.path import join
from tempfile import mkdtemp
from unittest.mock import MagicMock, patch, ANY

from nose.tools import assert_equals

from data.detector_execution import DetectOnlyExecution, MineAndDetectExecution, Result, DetectorExecution, DetectorMode
from data.runner_interface import NoInterface
from data.finding import Finding
from data.findings_filters import PotentialHits, AllFindings, FindingsFilter
from data.project_compile import ProjectCompile
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_misuse, create_version, create_project
from utils.io import remove_tree
from utils.shell import CommandFailedError


class DetectorExecutionTestImpl(DetectorExecution):
    def _get_findings_path(self):
        return "-findings-"

    def _load_findings(self):
        pass

    def _get_detector_arguments(self, project_compile: ProjectCompile):
        return dict()


@patch("data.detector_execution.read_yaml_if_exists")
class TestExecutionState:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-run-test_')
        self.findings_path = join(self.temp_dir, "-findings-")

        self.detector = StubDetector()
        self.version = create_version("-v-")
        self.findings_base_path = "-findings-"

        self.uut = DetectorExecutionTestImpl(DetectorMode.detect_only, self.detector, self.version,
                                             self.findings_base_path, AllFindings())

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_run_outdated(self, read_run_info):
        self.detector.md5 = "-md5-"
        read_run_info.return_value = {"md5": "-old-md5-"}

        uut = DetectorExecutionTestImpl(DetectorMode.detect_only, self.detector, self.version, self.findings_base_path,
                                        AllFindings())

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

        execution = MineAndDetectExecution(self.detector, self.version, self.findings_path, AllFindings())

        assert execution.is_success()
        assert_equals(execution.runtime, "23.42")
        assert_equals(execution.message, "-arbitrary text-")


@patch("data.detector_execution.write_yaml")
class TestDetectorExecution:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version = create_version("-version-", project=create_project("-project-"))
        self.detector = StubDetector()
        self.findings_base_path = "-findings-"

        self.logger = logging.getLogger("test")

        self.uut = DetectorExecutionTestImpl(DetectorMode.detect_only, self.detector, self.version,
                                             self.findings_base_path, AllFindings())

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

    def test_result_error_when_missing_runner_interface(self, write_yaml_mock):
        self.detector.runner_interface = NoInterface("-cli_version-")

        self.uut.execute("-compiles", 42, self.logger)

        write_yaml_mock.assert_called_with(
            {
                'result': 'error',
                'message': "No compatible runner interface for version -cli_version-",
                'md5': self.detector.md5,
                'runtime': ANY
            },
            file='-findings-/run.yml'
        )

class TestDetectorExecutionLoadFindings:
    @patch("data.detector_execution.open_yamls_if_exists")
    def test_adds_rank(self, read_yamls_mock):
        read_yamls_mock.return_value.__enter__.return_value = [{"name": "f1"}, {"name": "f2"}]
        execution = DetectorExecution(DetectorMode.mine_and_detect, None, None, "-findings-base-path-", FindingsFilter())
        execution._get_findings_path = lambda: ""

        findings = execution._load_findings()

        assert_equals(findings, [
            Finding({"name": "f1", "rank": 0}),
            Finding({"name": "f2", "rank": 1})
        ])


@patch("data.detector_execution.write_yaml")
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
                                       PotentialHits(self.misuse))

    def test_execute_per_misuse(self, get_dependencies_classpath_mock, write_yaml_mock):
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

        self.detector.runner_interface.execute.assert_called_with(
            self.version,
            {
                'target' : target,
                'run_info' : run_info,
                'detector_mode' : "1",
                'training_src_path' : training_src_path,
                'training_classpath' : training_classpath,
                'target_src_path' : target_src_path,
                'target_classpath' : target_classpath,
                'dep_classpath' : dependencies_classpath + ":" + original_classpath
            },
            42, self.logger)


@patch("data.detector_execution.write_yaml")
@patch("data.project_compile.ProjectCompile.get_dependency_classpath")
class TestMineAndDetectExecution:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version = create_version("-version-", project=create_project("-project-"))
        self.detector = StubDetector()
        self.findings_base_path = "-findings-"

        self.logger = logging.getLogger("test")

        self.uut = MineAndDetectExecution(self.detector, self.version, self.findings_base_path,
                                          AllFindings())

    def test_execute(self, get_dependencies_classpath_mock, write_yaml_mock):
        jar = self.detector.jar_path
        findings_path = join("-findings-", "mine_and_detect", "StubDetector", "-project-", "-version-")
        target = join(findings_path, "findings.yml")
        run_info = join(findings_path, "run.yml")
        compiles_path = join("-compiles-", "-project-", "-version-")
        target_src_path = join(compiles_path, "original-src")
        target_classpath = join(compiles_path, "original-classes")
        original_classpath = join(compiles_path, "original-classes.jar")
        dependencies_classpath = "-dependencies-classpath-"
        get_dependencies_classpath_mock.return_value = dependencies_classpath

        self.uut.execute("-compiles-", 42, self.logger)

        self.detector.runner_interface.execute.assert_called_with(
                self.version,
                {
                    'target': target,
                    'run_info': run_info,
                    'detector_mode': "0",
                    'target_src_path': target_src_path,
                    'target_classpath': target_classpath,
                    'dep_classpath': '{}:{}'.format(dependencies_classpath, original_classpath)
                },
                42, self.logger)
