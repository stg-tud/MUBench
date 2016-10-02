import logging
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp
from typing import Dict
from typing import List
from unittest import mock
from unittest.mock import MagicMock, PropertyMock

from nose.tools import assert_equals

from benchmark.data.finding import Finding
from benchmark.data.findings_filters import AllFindings, PotentialHits
from benchmark.data.run import Run
from benchmark.data.run_execution import RunExecutionState, VersionExecution, DetectorMode, MisuseExecution, \
    RunExecution
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

        run = Run([VersionExecution(DetectorMode.mine_and_detect, self.detector, self.version, self.findings_path,
                                    AllFindings(self.detector))])

        assert run.is_error()

    def test_timeout(self):
        self.write_run_file({"result": "timeout"})

        run = Run([VersionExecution(DetectorMode.mine_and_detect, self.detector, self.version, self.findings_path,
                                    AllFindings(self.detector))])

        assert run.is_timeout()

    def test_success(self):
        self.write_run_file({"result": "success"})

        run = Run([VersionExecution(DetectorMode.mine_and_detect, self.detector, self.version, self.findings_path,
                                    AllFindings(self.detector))])

        assert run.is_success()

    def test_run_outdated(self):
        with mock.patch('detectors.dummy.dummy.DummyDetector.md5', new_callable=PropertyMock) as mock_md5:
            mock_md5.return_value = "-md5-"
            detector = DummyDetector("-detectors-")

            state = RunExecutionState(detector, "")

            assert state.is_outdated()

    def test_run_up_to_date(self):
        state = RunExecutionState(self.detector, "")
        state._detector_md5 = self.detector.md5

        assert not state.is_outdated()

    def test_error_is_failure(self):
        state = RunExecutionState(self.detector, "")
        state.is_error = lambda: True
        state.is_timeout = lambda: False

        assert state.is_failure()

    def test_timeout_is_failure(self):
        state = RunExecutionState(self.detector, "")
        state.is_timeout = lambda: True
        state.is_error = lambda: False

        assert state.is_failure()

    def test_falls_back_to_method_name_if_no_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(p.A)"}])

    def test_matches_only_on_signature_if_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(A)"}, {"method": "method(B)"}])

    def test_metadata(self):
        self.write_run_file({"result": "success", "runtime": "23.42", "message": "-arbitrary text-"})

        execution = VersionExecution(DetectorMode.mine_and_detect, self.detector, self.version, self.findings_path,
                                     AllFindings(self.detector))

        assert execution.state.is_success()
        assert_equals(execution.state.runtime, "23.42")
        assert_equals(execution.state.message, "-arbitrary text-")

    def test_execute(self):
        execution = VersionExecution(DetectorMode.mine_and_detect, self.detector, self.version, "-findings-",
                                     AllFindings(self.detector))

        execution.execute("-compiles-", 42, self.logger)

        Shell.exec.assert_called_with('java -jar "-detectors-/dummy/dummy.jar" '
                                      'target "-findings-/mine_and_detect/dummy/-project-/-version-/findings.yml" '
                                      'run_info "-findings-/mine_and_detect/dummy/-project-/-version-/run.yml" '
                                      'detector_mode "0" '
                                      'target_src_path "-compiles-/-project-/-version-/original-src" '
                                      'target_classpath "-compiles-/-project-/-version-/original-classes"',
                                      logger=self.logger,
                                      timeout=42)

    def test_execute_per_misuse(self):
        run = MisuseExecution(DetectorMode.detect_only, self.detector, self.version, self.misuse, "-findings-",
                              PotentialHits(self.detector, self.misuse))

        run.execute("-compiles-", 42, self.logger)

        Shell.exec.assert_called_with('java -jar "-detectors-/dummy/dummy.jar" '
                                      'target "-findings-/detect_only/dummy/-project-/-version-/-misuse-/findings.yml" '
                                      'run_info "-findings-/detect_only/dummy/-project-/-version-/-misuse-/run.yml" '
                                      'detector_mode "1" '
                                      'training_src_path "-compiles-/-project-/-version-/patterns-src/-misuse-" '
                                      'training_classpath "-compiles-/-project-/-version-/patterns-classes/-misuse-" '
                                      'target_src_path "-compiles-/-project-/-version-/misuse-src" '
                                      'target_classpath "-compiles-/-project-/-version-/misuse-classes"',
                                      logger=self.logger,
                                      timeout=42)

    def assert_potential_hit(self, findings):
        run = VersionExecution(DetectorMode.detect_only, self.detector, self.version, "",
                               PotentialHits(self.detector, self.misuse))
        run._load_findings = lambda: self.create_findings(findings)
        assert run.findings

    def create_findings(self, findings_data: List[Dict[str, str]]):
        for finding in findings_data:
            if "file" not in finding:
                finding["file"] = self.misuse.location.file
            if "method" not in finding:
                finding["method"] = self.misuse.location.method

        return list(map(lambda data: Finding(data), findings_data))

    def write_run_file(self, run_data):
        write_yaml(run_data, join(self.findings_path,
                                  DetectorMode.mine_and_detect.name, self.detector.id,
                                  self.version.project_id, self.version.version_id, RunExecution.RUN_FILE))
