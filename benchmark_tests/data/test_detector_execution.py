import logging
from os.path import join
from unittest.mock import MagicMock

from benchmark.data.detector_execution import MisuseExecution, DetectorMode, VersionExecution
from benchmark.data.findings_filters import PotentialHits, AllFindings
from benchmark.utils.shell import Shell
from benchmark_tests.test_utils.data_util import create_misuse, create_version, create_project
from detectors.dummy.dummy import DummyDetector


class TestDetectOnlyExecution:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('-misuse-', meta={"location": {"file": "a", "method": "m()"}})
        self.version = create_version("-version-", misuses=[self.misuse], project=create_project("-project-"))
        self.detector = DummyDetector("-detectors-")

        self.logger = logging.getLogger("test")

        self.__orig_shell_exec = Shell.exec
        Shell.exec = MagicMock()

    def test_execute_per_misuse(self):
        jar = join("-detectors-", "dummy", "dummy.jar")
        target = join("-findings-", "detect_only", "dummy", "-project-", "-version-", "-misuse-", "findings.yml")
        run_info = join("-findings-", "detect_only", "dummy", "-project-", "-version-", "-misuse-", "run.yml")
        training_src_path = join("-compiles-", "-project-", "-version-", "patterns-src", "-misuse-")
        training_classpath = join("-compiles-", "-project-", "-version-", "patterns-classes", "-misuse-")
        target_src_path = join("-compiles-", "-project-", "-version-", "misuse-src")
        target_classpath = join("-compiles-", "-project-", "-version-", "misuse-classes")

        run = MisuseExecution(DetectorMode.detect_only, self.detector, self.version, self.misuse, "-findings-",
                              PotentialHits(self.detector, self.misuse))

        run.execute("-compiles-", 42, self.logger)

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

        self.logger = logging.getLogger("test")

        self.__orig_shell_exec = Shell.exec
        Shell.exec = MagicMock()

    def test_execute(self):
        jar = join("-detectors-", "dummy", "dummy.jar")
        target = join("-findings-", "mine_and_detect", "dummy", "-project-", "-version-", "findings.yml")
        run_info = join("-findings-", "mine_and_detect", "dummy", "-project-", "-version-", "run.yml")
        target_src_path = join("-compiles-", "-project-", "-version-", "original-src")
        target_classpath = join("-compiles-", "-project-", "-version-", "original-classes")

        execution = VersionExecution(DetectorMode.mine_and_detect, self.detector, self.version, "-findings-",
                                     AllFindings(self.detector))

        execution.execute("-compiles-", 42, self.logger)

        Shell.exec.assert_called_with('java -jar "{}" '.format(jar) +
                                      'target "{}" '.format(target) +
                                      'run_info "{}" '.format(run_info) +
                                      'detector_mode "0" ' +
                                      'target_src_path "{}" '.format(target_src_path) +
                                      'target_classpath "{}"'.format(target_classpath),
                                      logger=self.logger,
                                      timeout=42)
