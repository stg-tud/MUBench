import logging
from collections import OrderedDict
from distutils.version import StrictVersion
from enum import Enum, IntEnum
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
        matching_interfaces = [i for i in interfaces if i.version() == requested_version]
        if matching_interfaces:
            return matching_interfaces[0](jar_path, java_options)
        else:
            return NoInterface(requested_version)

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
        self.logger.warning("The detector uses a legacy interface.")
        self.logger.info("The following changes were made since its release:")
        self._log_changes()

    def _log_changes(self):
        logger = logging.getLogger("runner_interface.changelogs")

        interfaces = RunnerInterface._get_interfaces()
        later_interfaces = [i for i in interfaces if i.version() > self.version()]
        later_interfaces.sort(key=lambda i: i.version())
        for index, later_interface in enumerate(later_interfaces):
            from_ = later_interfaces[index-1].version()
            to = later_interface.version()
            logger.info("{} => {}:".format(from_, to))
            logger.info(later_interface.changelog())

    def is_legacy(self) -> bool:
        return self.version() < self.__get_latest_version()

    @staticmethod
    def _get_interfaces() -> List['RunnerInterface']:
        return RunnerInterface.__subclasses__()

    @staticmethod
    def __get_latest_version() -> StrictVersion:
        versions = [interface.version() for interface in \
                RunnerInterface._get_interfaces()]
        return sorted(versions)[-1]


class NoInterface():
    def __init__(self, requested_cli_version: StrictVersion):
        self._requested_cli_version = requested_cli_version

    def execute(self, *_):
        raise NoCompatibleRunnerInterface(self._requested_cli_version)

    def is_legacy(self):
        return False


class RunnerInterface_0_0_8(RunnerInterface):
    _VALID_KEYS = [
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
    def version() -> StrictVersion:
        return StrictVersion("0.0.8")

    @staticmethod
    def changelog() -> str:
        return "Oldest version."

    def execute(self, version: ProjectVersion, detector_arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        detector_arguments = self._filter_args(detector_arguments, logger)
        command = self._get_command(version, detector_arguments)
        Shell.exec(command, logger=logger, timeout=timeout)

    @staticmethod
    def _filter_args(args: Dict[str, str], logger: Logger) -> Dict[str, str]:
        valid_args = OrderedDict()
        for key, value in args.items():
            if key in RunnerInterface_0_0_8._VALID_KEYS:
                valid_args[key] = value
            else:
                logger.debug("Detector uses legacy CLI: argument %s with value %s will not be passed to the detector.", key, value)
        return valid_args

    def _get_command(self, version: ProjectVersion, detector_arguments: Dict[str, str]) -> str:
        detector_invocation = ["java"] + self.java_options + ["-jar", _quote(self.jar_path)]
        detector_arguments = self._get_cli_args(detector_arguments)
        command = detector_invocation + _as_list(detector_arguments)
        command = " ".join(command)
        return command

    @staticmethod
    def _get_cli_args(detector_arguments: Dict[str, str]) -> Dict[str, str]:
        args = OrderedDict()
        for key, value in detector_arguments.items():
            args[key] = _quote(value)
        return args

class NoCompatibleRunnerInterface(Exception):
    def __init__(self, version: StrictVersion):
        super().__init__("No compatible runner interface for version {}".format(version))
