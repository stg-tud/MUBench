import logging
from collections import OrderedDict
from distutils.version import StrictVersion
from os.path import join
from unittest.mock import MagicMock, patch

from nose.tools import assert_equals, assert_true, assert_false, assert_raises

from data.runner_interface import RunnerInterface, RunnerInterface_0_0_8, RunnerInterface_0_0_11
from tests.test_utils.data_util import create_version
from tests.test_utils.runner_interface_test_impl import RunnerInterfaceTestImpl


class TestRunnerInterface:
    def setup(self):
        self.test_interfaces = [RunnerInterfaceTestImpl]

        self._orig_get_interfaces = RunnerInterface._get_interfaces
        RunnerInterface._get_interfaces = lambda: self.test_interfaces

    def teardown(self):
        RunnerInterface._get_interfaces = self._orig_get_interfaces

    def test_get_interface_version(self):
        actual = RunnerInterface.get(RunnerInterfaceTestImpl.TEST_VERSION, "", [])
        assert_true(isinstance(actual, RunnerInterfaceTestImpl))

    def test_selects_closest_version(self):
        class LegacyInterface(RunnerInterfaceTestImpl): pass
        LegacyInterface.version = lambda *_: StrictVersion("0.0.9")
        class LatestInterface(RunnerInterfaceTestImpl): pass
        LatestInterface.version = lambda *_: StrictVersion("0.0.11")
        self.test_interfaces = [LatestInterface, LegacyInterface]

        actual = RunnerInterface.get(StrictVersion("0.0.12"), "", [])

        assert_equals(LatestInterface, type(actual))

    def test_uses_most_recent_interface_on_no_compatible_version(self):
        class LatestInterface(RunnerInterfaceTestImpl): pass
        LatestInterface.version = lambda *_: StrictVersion("0.0.12")
        self.test_interfaces = [LatestInterface]

        actual = RunnerInterface.get(StrictVersion("0.0.6"), "", [])

        assert_equals(LatestInterface, type(actual))


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

        actual_changes = LegacyInterface('', [])._get_changelogs()

        expected_changes = ["0.0.1 => 0.0.2:", "-changelog-"]
        assert_equals(expected_changes, actual_changes)

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

        actual_changes = LegacyInterface('', [])._get_changelogs()

        expected_changes = ["0.0.1 => 0.0.2:", "-changelog1-",
                            "0.0.2 => 0.0.3:", "-changelog2-"]
        assert_equals(expected_changes, actual_changes)

    def test_no_logs_on_empty_changelogs(self):
        class LegacyInterface(RunnerInterfaceTestImpl): pass

        class NewerInterface(RunnerInterfaceTestImpl): pass

        LegacyInterface.version = lambda *_: StrictVersion("0.0.1")
        NewerInterface.version = lambda *_: StrictVersion("0.0.2")
        NewerInterface.changelog = lambda *_: None
        self.test_interfaces = [LegacyInterface, NewerInterface]
        uut = LegacyInterface('', [])
        uut.logger = MagicMock()

        uut._log_legacy_warning()

        uut.logger.info.assert_not_called()
        uut.logger.warning.assert_not_called()


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
        training_src_path = join(compiles_path, "correct-usages-src", "-misuse-")
        training_classpath = join(compiles_path, "correct-usages-classes", "-misuse-")
        target_src_path = join(compiles_path, "misuse-src")
        target_classpath = join(compiles_path, "misuse-classes")
        dependencies_classpath = "-dependencies-classpath-"

        detector_args = OrderedDict([
                ("target", target),
                ("run_info", run_info),
                ("detector_mode", "1"),
                ("training_src_path", training_src_path),
                ("training_classpath", training_classpath),
                ("target_src_path", [target_src_path]),
                ("target_classpath", [target_classpath]),
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

    def test_raises_on_multiple_target_paths(self, _):
        jar = "-detector-"
        compiles_path = join("-compiles-", "-project-", "-version-")
        target_src_paths = [join(compiles_path, "misuse-src"), join(compiles_path, "misuse-tests-src")]
        target_classpaths = [join(compiles_path, "misuse-classes"), join(compiles_path, "misuse-tests-src")]

        detector_args = OrderedDict([
            ("target_src_path", target_src_paths),
            ("target_classpath", target_classpaths),
        ])

        uut = RunnerInterface_0_0_8(jar, [])

        assert_raises(ValueError, uut.execute, self.version, detector_args, timeout=42, logger=self.logger)


@patch("data.runner_interface.Shell")
class TestRunnerInterface_0_0_11:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.uut = RunnerInterface_0_0_11("-detector-", [])
        self.logger = logging.getLogger("test")
        self.version = create_version("-version-")

    def test_joins_target_paths(self, shell_mock):
        jar = "-detector-"
        compiles_path = join("-compiles-", "-project-", "-version-")
        target_src_paths = [join(compiles_path, "misuse-src"), join(compiles_path, "misuse-tests-src")]
        target_classpaths = [join(compiles_path, "misuse-classes"), join(compiles_path, "misuse-tests-src")]

        detector_args = OrderedDict([
            ("target_src_path", target_src_paths),
            ("target_classpath", target_classpaths),
        ])

        uut = RunnerInterface_0_0_11(jar, [])
        uut.execute(self.version, detector_args, timeout=42, logger=self.logger)

        shell_mock.exec.assert_called_with('java -jar "{}" '.format(jar) +
                                           'target_src_path "{}" '.format(":".join(target_src_paths)) +
                                           'target_classpath "{}"'.format(":".join(target_classpaths)),
                                           logger=self.logger, timeout=42)
