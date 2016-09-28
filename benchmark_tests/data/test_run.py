import logging
from os.path import join
from tempfile import mkdtemp
from typing import Dict
from typing import List
from unittest.mock import MagicMock

from nose.tools import assert_equals
from shutil import rmtree

from benchmark.data.finding import Finding
from benchmark.data.run import Run, PerMisuseRun, VersionRun, Result, MisuseWithPatternRun, DetectorMode
from benchmark.utils.io import write_yaml
from benchmark.utils.shell import Shell
from benchmark_tests.test_utils.data_util import create_misuse, create_version, create_project
from detectors.dummy.dummy import DummyDetector


class TestRun:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('misuse', meta={"location": {"file": "a", "method": "m()"}})
        self.version = create_version("-version-", misuses=[self.misuse])
        self.detector = DummyDetector("-detectors-")

    def test_run_outdated(self):
        run = Run(self.detector, self.version)

        assert run.is_outdated()

    def test_run_up_to_date(self):
        run = Run(self.detector, self.version)
        run._detector_md5 = self.detector.md5

        assert not run.is_outdated()

    def test_error_is_failure(self):
        run = Run(self.detector, self.version)
        run.is_error = lambda: True
        run.is_timeout = lambda: False

        assert run.is_failure()

    def test_timeout_is_failure(self):
        run = Run(self.detector, self.version)
        run.is_timeout = lambda: True
        run.is_error = lambda: False

        assert run.is_failure()

    def test_falls_back_to_method_name_if_no_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(p.A)"}])

    def test_matches_only_on_signature_if_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(A)"}, {"method": "method(B)"}])

    def assert_potential_hit(self, findings):
        run = Run(self.detector, self.version)
        run._load_findings = lambda: self.create_findings(findings)
        assert run.get_potential_hits(self.misuse)

    def create_findings(self, findings_data: List[Dict[str, str]]):
        for finding in findings_data:
            if "file" not in finding:
                finding["file"] = self.misuse.location.file
            if "method" not in finding:
                finding["method"] = self.misuse.location.method

        return list(map(lambda data: Finding(data), findings_data))


class TestVersionRun:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-run-test_')
        self.findings_path = join(self.temp_dir, "-findings-")

        self.logger = logging.getLogger("test")
        self.detector = DummyDetector("-detectors-")
        self.version = create_version("-version-", project=create_project("-project-"))

        self.__orig_shell_exec = Shell.exec
        Shell.exec = MagicMock()

    def teardown(self):
        rmtree(self.temp_dir)
        Shell.exec = self.__orig_shell_exec

    def test_not_run(self):
        run = VersionRun(self.detector, self.findings_path, self.version)

        assert_equals(run.result, None)
        assert not run.is_success()
        assert not run.is_failure()

    def test_error(self):
        self.write_run_file({"result": "error"})

        run = VersionRun(self.detector, self.findings_path, self.version)

        assert run.is_error()

    def test_timeout(self):
        self.write_run_file({"result": "timeout"})

        run = VersionRun(self.detector, self.findings_path, self.version)

        assert run.is_timeout()

    def test_success(self):
        self.write_run_file({"result": "success"})

        run = VersionRun(self.detector, self.findings_path, self.version)

        assert run.is_success()

    def test_metadata(self):
        self.write_run_file({"result": "success", "runtime": "23.42", "message": "-arbitrary text-"})

        run = VersionRun(self.detector, self.findings_path, self.version)

        assert_equals(run.result, Result.success)
        assert_equals(run.runtime, "23.42")
        assert_equals(run.message, "-arbitrary text-")

    def test_execute(self):
        run = VersionRun(self.detector, "-findings-", self.version)

        run.execute("-compiles-", 42, self.logger)

        Shell.exec.assert_called_with('java -jar "-detectors-/dummy/dummy.jar" '
                                      'target "-findings-/mine_and_detect/dummy/-project-/-version-/findings.yml" '
                                      'run_info "-findings-/mine_and_detect/dummy/-project-/-version-/run.yml" '
                                      'detector_mode "0" '
                                      'target_src_path "-compiles-/-project-/-version-/original-src" '
                                      'target_classpath "-compiles-/-project-/-version-/original-classes"',
                                      logger=self.logger,
                                      timeout=42)

    def write_run_file(self, run_data):
        write_yaml(run_data, join(self.findings_path,
                                  DetectorMode.mine_and_detect.name, self.detector.id,
                                  self.version.project_id, self.version.version_id, "run.yml"))


class TestMisuseWithPatternRun:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.__orig_shell_exec = Shell.exec
        Shell.exec = MagicMock()

    def teardown(self):
        Shell.exec = self.__orig_shell_exec

    def test_execute(self):
        misuse = create_misuse("-misuse-")
        version = create_version("-version-", project=create_project("-project-"))
        logger = logging.getLogger("test")
        run = MisuseWithPatternRun(DummyDetector("-detectors-"), "-findings-", version, misuse)

        run.execute("-compiles-", 42, logger)

        Shell.exec.assert_called_with('java -jar "-detectors-/dummy/dummy.jar" '
                                      'target "-findings-/detect_only/dummy/-project-/-version-/-misuse-/findings.yml" '
                                      'run_info "-findings-/detect_only/dummy/-project-/-version-/-misuse-/run.yml" '
                                      'detector_mode "1" '
                                      'training_src_path "-compiles-/-project-/-version-/patterns-src/-misuse-" '
                                      'training_classpath "-compiles-/-project-/-version-/patterns-classes/-misuse-" '
                                      'target_src_path "-compiles-/-project-/-version-/misuse-src" '
                                      'target_classpath "-compiles-/-project-/-version-/misuse-classes"',
                                      logger=logger,
                                      timeout=42)


class TestPerMisuseRun:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.run = PerMisuseRun(DummyDetector("-detectors-"), "-findings-", create_version("-version-"))
        self.misuse_run1 = MagicMock(spec=Run)
        self.misuse_run2 = MagicMock(spec=Run)
        self.run._PerMisuseRun__misuse_runs = [self.misuse_run1, self.misuse_run2]

    def test_execute(self):
        logger = logging.getLogger("test")

        self.run.execute("-compiles-", 42, logger)

        self.misuse_run1.execute.assert_called_with("-compiles-", 42, logger)
        self.misuse_run2.execute.assert_called_with("-compiles-", 42, logger)
