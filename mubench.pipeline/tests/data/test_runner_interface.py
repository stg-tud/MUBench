import logging
from collections import OrderedDict
from distutils.version import StrictVersion
from os.path import join
from tempfile import mkdtemp
from unittest import mock
from unittest.mock import MagicMock, PropertyMock, patch, call

from nose.tools import assert_equals, assert_true, assert_false, assert_raises

from data.runner_interface import RunnerInterface, RunnerInterface_0_0_8, NoCompatibleRunnerInterface
from tests.data.stub_detector import StubDetector
from utils.io import remove_tree, write_yaml
from utils.shell import Shell, CommandFailedError
from tests.test_utils.data_util import create_misuse, create_version, create_project
from tests.test_utils.runner_interface_test_impl import RunnerInterfaceTestImpl


class TestRunnerInterface:
    def setup(self):
        self.test_interfaces = [RunnerInterfaceTestImpl]

        self._orig_get_interfaces = RunnerInterface._get_interfaces
        RunnerInterface._get_interfaces = lambda: self.test_interfaces

    def teardown(self):
        RunnerInterface._get_interfaces = self._orig_get_interfaces

    def test_get_interface_version(self):
        actual = RunnerInterface.get(RunnerInterfaceTestImpl.TEST_VERSION, "", dict())
        assert_true(isinstance(actual, RunnerInterfaceTestImpl))

    def test_get_interface_version_raises_for_unavailable_version(self):
        assert_raises(NoCompatibleRunnerInterface, RunnerInterface.get, "1000.90.42", "", dict())

    def test_interface_is_legacy(self):
        class LatestInterface(RunnerInterfaceTestImpl): pass
        LatestInterface.version = lambda *_: StrictVersion("0.0.1")
        class LegacyInterface(RunnerInterfaceTestImpl): pass
        LegacyInterface.version = lambda *_: StrictVersion("0.0.0")
        self.test_interfaces = [LatestInterface, LegacyInterface]

        assert_true(LegacyInterface("", []).is_legacy())

    def test_latest_interface_is_not_legacy(self):
        class LatestInterface(RunnerInterfaceTestImpl): pass
        LatestInterface.version = lambda *_: StrictVersion("0.0.1")
        class LegacyInterface(RunnerInterfaceTestImpl): pass
        LegacyInterface.version = lambda *_: StrictVersion("0.0.0")
        self.test_interfaces = [LatestInterface, LegacyInterface]

        assert_false(LatestInterface("", []).is_legacy())

    def test_handles_interfaces_without_version(self):
        class InterfaceBaseImpl(RunnerInterface): pass
        assert InterfaceBaseImpl not in self._orig_get_interfaces()

    def test_finds_interfaces_recursively(self):
        class InterfaceBase(RunnerInterface): pass
        class InterfaceBaseImpl(InterfaceBase): pass
        InterfaceBaseImpl.version = lambda *_: StrictVersion("0.0.0")

        assert InterfaceBaseImpl in self._orig_get_interfaces()

    def test_logs_legacy_changelogs(self):
        class LegacyInterface(RunnerInterfaceTestImpl): pass
        class LatestInterface(RunnerInterfaceTestImpl): pass
        LegacyInterface.version = lambda *_: StrictVersion("0.0.1")
        LatestInterface.version = lambda *_: StrictVersion("0.0.2")
        LatestInterface.changelog = lambda *_: "-changelog-"
        self.test_interfaces = [LatestInterface, LegacyInterface]
        logger = MagicMock()

        LegacyInterface('', [])._log_changes(logger)

        expected_calls = [call("0.0.1 => 0.0.2:"), call("-changelog-")]
        logger.info.assert_has_calls(expected_calls)

    def test_logs_multiple_legacy_changelogs(self):
        class LegacyInterface(RunnerInterfaceTestImpl): pass
        class Interface_0_0_2(RunnerInterfaceTestImpl): pass
        class Interface_0_0_3(RunnerInterfaceTestImpl): pass
        LegacyInterface.version = lambda *_: StrictVersion("0.0.1")
        Interface_0_0_2.version = lambda *_: StrictVersion("0.0.2")
        Interface_0_0_2.changelog = lambda *_: "-changelog1-"
        Interface_0_0_3.version = lambda *_: StrictVersion("0.0.3")
        Interface_0_0_3.changelog = lambda *_: "-changelog2-"
        self.test_interfaces = [LegacyInterface, Interface_0_0_2, Interface_0_0_3]
        logger = MagicMock()

        LegacyInterface('', [])._log_changes(logger)

        expected_calls = [call("0.0.1 => 0.0.2:"), call("-changelog1-"),
                          call("0.0.2 => 0.0.3:"), call("-changelog2-")]
        logger.info.assert_has_calls(expected_calls)


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
