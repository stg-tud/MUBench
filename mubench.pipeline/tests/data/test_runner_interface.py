import logging
from collections import OrderedDict
from os.path import join
from tempfile import mkdtemp
from unittest import mock
from unittest.mock import MagicMock, PropertyMock, patch

from nose.tools import assert_equals, assert_true, assert_raises

from data.runner_interface import NoInterface, RunnerInterface, RunnerInterface_0_0_8, NoCompatibleRunnerInterface
from tests.data.stub_detector import StubDetector
from utils.io import remove_tree, write_yaml
from utils.shell import Shell, CommandFailedError
from tests.test_utils.data_util import create_misuse, create_version, create_project
from tests.test_utils.runner_interface_test_impl import RunnerInterfaceTestImpl

class TestRunnerInterface:
    def test_get_interface_version(self):
        actual = RunnerInterface.get(RunnerInterfaceTestImpl.TEST_VERSION, "", dict())
        assert_true(isinstance(actual, RunnerInterfaceTestImpl))

    def test_get_interface_version_default_for_none(self):
        actual = RunnerInterface.get(None, "", dict())
        assert_true(isinstance(actual, NoInterface))

    def test_get_interface_version_default_for_unavailable_version(self):
        actual = RunnerInterface.get("-unavailable_version-", "", dict())
        assert_true(isinstance(actual, NoInterface))

class TestNoInterface:
    def test_execute_raises_exception(self):
        uut = NoInterface("-version-")
        assert_raises(NoCompatibleRunnerInterface, uut.execute, [])

    def test_exception_contains_version(self):
        uut = NoInterface("-version-")
        try:
            uut.execute()
        except NoCompatibleRunnerInterface as e:
            assert_equals(e.version, "-version-")

@patch("data.runner_interface.Shell")
class TestRunnerInterface_0_0_8:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.uut = RunnerInterface_0_0_8("-detector-", [])
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

        detector_args = OrderedDict([
                ("target", target),
                ("run_info", run_info),
                ("detector_mode", "1"),
                ("training_src_path", training_src_path),
                ("training_classpath", training_classpath),
                ("target_src_path", target_src_path),
                ("target_classpath", target_classpath),
                ("dep_classpath", dependencies_classpath)
            ])

        uut = RunnerInterface_0_0_8(jar, [])

        uut.execute(self.version, detector_args, timeout=42, logger=self.logger)

        shell_mock.exec.assert_called_with('java -jar "{}" '.format(jar) +
                                           'target "{}" '.format(target) +
                                           'run_info "{}" '.format(run_info) +
                                           'detector_mode "1" ' +
                                           'training_src_path "{}" '.format(training_src_path) +
                                           'training_classpath "{}" '.format(training_classpath) +
                                           'target_src_path "{}" '.format(target_src_path) +
                                           'target_classpath "{}" '.format(target_classpath) +
                                           'dep_classpath "{}"'.format(dependencies_classpath),
                                           logger=self.logger, timeout=42)

    def test_filters_incompatible_args(self, shell_mock):
        jar = "-detector-"
        uut = RunnerInterface_0_0_8(jar, [])

        uut.execute(self.version, {"-incompatible-" : "-value-"}, timeout=42, logger=self.logger)

        shell_mock.exec.assert_called_with('java -jar "{}"'.format(jar),
                                           logger=self.logger, timeout=42)
