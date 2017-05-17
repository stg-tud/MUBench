import logging
from os.path import join
from tempfile import mkdtemp
from unittest import mock
from unittest.mock import MagicMock, PropertyMock, patch

from nose.tools import assert_equals, assert_true

from data.runner_interface import RunnerInterface, RunnerInterfaceV20170406
from tests.data.stub_detector import StubDetector
from utils.io import remove_tree, write_yaml
from utils.shell import Shell, CommandFailedError
from tests.test_utils.data_util import create_misuse, create_version, create_project
from tests.test_utils.runner_interface_test_impl import RunnerInterfaceTestImpl

class TestRunnerInterface:
    def test_get_interface_version(self):
        actual = RunnerInterface.get(RunnerInterfaceTestImpl.TEST_VERSION, "", dict())
        assert_true(isinstance(actual, RunnerInterfaceTestImpl))

@patch("data.runner_interface.Shell")
class TestRunnerInterfaceV20170406:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.uut = RunnerInterfaceV20170406("-detector-", [])
        self.logger = logging.getLogger("test")
        self.version = create_version("-version-")

    def test_execute_per_misuse(self, shell_mock):
        jar = "-detector-"
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

        uut = RunnerInterfaceV20170406(jar, [])

        uut.execute(self.version,
            {
                "target" : target,
                "run_info" : run_info,
                "detector_mode" : "1",
                "training_src_path" : training_src_path,
                "training_classpath" : training_classpath,
                "target_src_path" : target_src_path,
                "target_classpath" : target_classpath,
                "dep_classpath" : dependencies_classpath
            },
            timeout=42, logger=self.logger)

        shell_mock.exec.assert_called_with('java -jar "{}" '.format(jar) +
                                           'dep_classpath "{}" '.format(dependencies_classpath) +
                                           'detector_mode "1" ' +
                                           'run_info "{}" '.format(run_info) +
                                           'target "{}" '.format(target) +
                                           'target_classpath "{}" '.format(target_classpath) +
                                           'target_src_path "{}" '.format(target_src_path) +
                                           'training_classpath "{}" '.format(training_classpath) +
                                           'training_src_path "{}"'.format(training_src_path),
                                           logger=self.logger, timeout=42)

    def test_filters_incompatible_args(self, shell_mock):
        jar = "-detector-"
        uut = RunnerInterfaceV20170406(jar, [])

        uut.execute(self.version, {"-incompatible-" : "-value-"}, timeout=42, logger=self.logger)

        shell_mock.exec.assert_called_with('java -jar "{}"'.format(jar),
                                           logger=self.logger, timeout=42)
