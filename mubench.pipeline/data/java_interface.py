from enum import Enum, IntEnum
from logging import Logger
from typing import Optional, List, Dict

from data.project_version import ProjectVersion
from utils.shell import Shell

def _quote(value: str):
    return "\"{}\"".format(value)

class JavaInterface:
    def __init__(self, jar_path: str, java_options: List[str]):
        self.jar_path = jar_path
        self.java_options = java_options

    @staticmethod
    def get(cli_version: str, jar_path: str, java_options: List[str]) -> 'JavaInterface':
        interfaces = JavaInterface.__subclasses__()
        matching_interfaces = [i for i in interfaces if i.version() == cli_version]
        if matching_interfaces:
            return matching_interfaces[0](jar_path, java_options)
        else:
            raise ValueError("No Java interface available for version " + cli_version)

    @staticmethod
    def version() -> str:
        raise NotImplementedError

    def execute(self, version: ProjectVersion, detector_arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        raise NotImplementedError

class JavaInterfaceV20170406(JavaInterface):
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
        return "20170406"

    def execute(self, version: ProjectVersion, detector_arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        detector_arguments = self._filter_args(detector_arguments, logger)
        command = self._get_command(version, detector_arguments)
        Shell.exec(command, logger=logger, timeout=timeout)

    @staticmethod
    def _filter_args(args: Dict[str, str], logger: Logger) -> Dict[str, str]:
        valid_args = dict()
        for key, value in args.items():
            if key in JavaInterfaceV20170406._VALID_KEYS:
                valid_args[key] = value
            else:
                logger.debug("Detector uses legacy CLI: argument %s with value %s will not be passed to the detector.", key, value)
        return valid_args 

    def _get_command(self, version: ProjectVersion, detector_arguments: Dict[str, str]) -> str:
        detector_invocation = ["java"] + self.java_options + ["-jar", _quote(self.jar_path)]
        detector_arguments = self._get_cli_args(detector_arguments)
        command = detector_invocation + detector_arguments
        command = " ".join(command)
        return command

    @staticmethod
    def _get_cli_args(detector_arguments: Dict[str, str]) -> List[str]:
        args = []
        for key, value in detector_arguments.items():
            args.append("{} {}".format(key, _quote(value)))
        return sorted(args)
