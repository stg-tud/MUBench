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
    @staticmethod
    def version() -> str:
        return "20170406"

    def execute(self, version: ProjectVersion, detector_arguments: Dict[str, str],
                timeout: Optional[int], logger: Logger):
        command = self._get_command(version, detector_arguments)
        Shell.exec(command, logger=logger, timeout=timeout)

    def _get_command(self, version: ProjectVersion, detector_arguments: Dict[str, str]) -> str:
        detector_invocation = ["java"] + self.java_options + ["-jar", _quote(self.jar_path)]
        command = detector_invocation + detector_arguments
        command = " ".join(command)
        return command
