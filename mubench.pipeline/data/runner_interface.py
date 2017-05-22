from collections import OrderedDict
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

    @staticmethod
    def get(cli_version: str, jar_path: str, java_options: List[str]) -> 'RunnerInterface':
        interfaces = RunnerInterface.__subclasses__()
        matching_interfaces = [i for i in interfaces if i.version() == cli_version]
        if matching_interfaces:
            return matching_interfaces[0](jar_path, java_options)
        else:
            raise ValueError("No Runner interface available for version " + cli_version)

    @staticmethod
    def version() -> str:
        raise NotImplementedError

    def execute(self, version: ProjectVersion, detector_arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        raise NotImplementedError

class RunnerInterfaceV20170406(RunnerInterface):
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
    def version() -> str:
        return "v20170406"

    def execute(self, version: ProjectVersion, detector_arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        detector_arguments = self._filter_args(detector_arguments, logger)
        command = self._get_command(version, detector_arguments)
        Shell.exec(command, logger=logger, timeout=timeout)

    @staticmethod
    def _filter_args(args: Dict[str, str], logger: Logger) -> Dict[str, str]:
        valid_args = OrderedDict()
        for key, value in args.items():
            if key in RunnerInterfaceV20170406._VALID_KEYS:
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
