import logging
from collections import OrderedDict
from distutils.version import StrictVersion
from logging import Logger
from typing import Optional, List, Dict

from data.project_version import ProjectVersion
from utils.shell import Shell


def _quote(value: str):
    return "\"{}\"".format(value)


def _as_list(dictionary: Dict) -> List:
    l = list()
    for key, value in dictionary.items():
        l.append(key)
        l.append(value)
    return l


class RunnerInterface:
    def __init__(self, jar_path: str, java_options: List[str]):
        self.jar_path = jar_path
        self.java_options = java_options
        self.logger = logging.getLogger("runner_interface")

        if self.is_legacy():
            self._log_legacy_warning()

    @staticmethod
    def get(requested_version: StrictVersion, jar_path: str, java_options: List[str]) -> 'RunnerInterface':
        interfaces = RunnerInterface._get_interfaces()
        for interface in sorted(interfaces, key=lambda i: i.version(), reverse=True):
            if interface.version() <= requested_version:
                return interface(jar_path, java_options)

    @staticmethod
    def version() -> StrictVersion:
        raise NotImplementedError

    @staticmethod
    def changelog() -> str:
        raise NotImplementedError

    def execute(self, version: ProjectVersion, detector_arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        raise NotImplementedError

    def _log_legacy_warning(self):
        changelogs = self._get_changelogs()
        if changelogs:
            self.logger.warning("The detector uses a legacy interface.")
            self.logger.info("The following changes were made since its release:")
            changes_logger = logging.getLogger("runner_interface.changelogs")
            for changelog in changelogs:
                changes_logger.info(changelog)

    def _get_changelogs(self):
        changes = []
        interfaces = RunnerInterface._get_interfaces()
        later_interfaces = [i for i in interfaces if i.version() > self.version()]
        later_interfaces.sort(key=lambda i: i.version())
        from_ = self.version()
        for later_interface in later_interfaces:
            to = later_interface.version()
            if later_interface.changelog():
                changes.append("{} => {}:".format(from_, to))
                changes.append(later_interface.changelog())
            from_ = later_interface.version()
        return changes

    def is_legacy(self) -> bool:
        return self.version() < self.__get_latest_version()

    @staticmethod
    def _get_interfaces() -> List['RunnerInterface']:
        interfaces_with_versions = []
        for interface in _get_subclasses_recursive(RunnerInterface):
            try:
                interface.version()
                interfaces_with_versions.append(interface)
            except NotImplementedError:
                continue

        return interfaces_with_versions

    @staticmethod
    def __get_latest_version() -> StrictVersion:
        versions = [interface.version() for interface in RunnerInterface._get_interfaces()]
        return sorted(versions)[-1]


def _get_subclasses_recursive(class_) -> List['RunnerInterface']:
    subclasses = []
    for subclass in class_.__subclasses__():
        subclasses.append(subclass)
        subclasses.extend(_get_subclasses_recursive(subclass))
    return subclasses


class CommandLineArgsRunnerInterface(RunnerInterface):
    @staticmethod
    def version() -> StrictVersion:
        raise NotImplementedError()

    @staticmethod
    def changelog() -> str:
        raise NotImplementedError()

    def execute(self, version: ProjectVersion, detector_arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        detector_arguments = self._filter_args(detector_arguments, logger)
        command = self._get_command(detector_arguments)
        Shell.exec(command, logger=logger, timeout=timeout)

    def _filter_args(self, args: Dict[str, str], logger: Logger) -> Dict[str, str]:
        valid_args = OrderedDict()
        for key, value in args.items():
            if key in self._get_supported_cli_args():
                valid_args[key] = value
            else:
                logger.warning("Detector uses legacy CLI: argument `%s` will not be passed to it.", key)
        return valid_args

    def _get_command(self, detector_arguments: Dict[str, str]) -> str:
        detector_invocation = ["java"] + self.java_options + ["-jar", _quote(self.jar_path)]
        detector_arguments = self._get_cli_args(detector_arguments)
        command = detector_invocation + _as_list(detector_arguments)
        command = " ".join(command)
        return command

    @staticmethod
    def _get_supported_cli_args():
        raise NotImplementedError()

    @staticmethod
    def _get_cli_args(detector_arguments: Dict[str, str]) -> Dict[str, str]:
        args = OrderedDict()
        for key, value in detector_arguments.items():
            args[key] = _quote(value)
        return args


# noinspection PyPep8Naming
class RunnerInterface_0_0_7(CommandLineArgsRunnerInterface):
    @staticmethod
    def version() -> StrictVersion:
        return StrictVersion("0.0.7")

    @staticmethod
    def changelog() -> str:
        return ""

    @staticmethod
    def _get_supported_cli_args():
        return [
            "target",
            "run_info",
            "detector_mode",
            "training_src_path",
            "training_classpath",
            "target_src_path",
            "target_classpath"
        ]


# noinspection PyPep8Naming
class RunnerInterface_0_0_8(CommandLineArgsRunnerInterface):
    @staticmethod
    def version() -> StrictVersion:
        return StrictVersion("0.0.8")

    @staticmethod
    def changelog() -> str:
        return "Pass dependency classpath to detectors as `dep_classpath`."

    @staticmethod
    def _get_supported_cli_args():
        return [
            "target",
            "run_info",
            "detector_mode",
            "training_src_path",
            "training_classpath",
            "target_src_path",
            "target_classpath",
            "dep_classpath"
        ]

    @staticmethod
    def _get_cli_args(detector_arguments: Dict[str, str]):
        target_src_paths = detector_arguments.get("target_src_path", ())
        target_classpaths = detector_arguments.get("target_classpath", ())

        if len(target_src_paths) > 1 or len(target_classpaths) > 1:
            raise ValueError("This legacy interface version can not handle multiple src/classes paths.")

        if len(target_src_paths) == 1:
            detector_arguments["target_src_path"] = target_src_paths[0]
        if len(target_classpaths) == 1:
            detector_arguments["target_classpath"] = target_classpaths[0]

        return CommandLineArgsRunnerInterface._get_cli_args(detector_arguments)


# noinspection PyPep8Naming
class RunnerInterface_0_0_10(RunnerInterface_0_0_8):
    @staticmethod
    def version():
        return StrictVersion("0.0.10")

    @staticmethod
    def changelog():
        return ""  # Only changed Java-side interface.


# noinspection PyPep8Naming
class RunnerInterface_0_0_11(RunnerInterface_0_0_10):
    @staticmethod
    def version():
        return StrictVersion("0.0.11")

    @staticmethod
    def changelog():
        return "Now handles multiple src/classes target paths."

    @staticmethod
    def _get_cli_args(detector_arguments: Dict[str, str]):
        detector_arguments["target_src_path"] = ":".join(detector_arguments["target_src_path"])
        detector_arguments["target_classpath"] = ":".join(detector_arguments["target_classpath"])
        return CommandLineArgsRunnerInterface._get_cli_args(detector_arguments)


# noinspection PyPep8Naming
class RunnerInterface_0_0_13(RunnerInterface_0_0_11):
    @staticmethod
    def version():
        return StrictVersion("0.0.13")

    @staticmethod
    def changelog():
        return ""  # Only changed Java-side interface.
