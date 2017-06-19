import logging
from typing import List

from utils.shell import Shell


class BuildCommand:
    def __init__(self, name: str, args: List[str]):
        self._name = name
        self.args = args

    @staticmethod
    def get(requested_command: str) -> 'BuildCommand':
        requested_command = requested_command.split(' ')
        requested_name = requested_command[0]
        args = requested_command[1:]

        commands = BuildCommand._get_implementations()
        matching_commands = [c for c in commands if
                             c.name() == requested_name]
        if len(matching_commands) == 1:
            matching_command = matching_commands[0]
            return matching_command(requested_name, args)
        if not matching_commands:
            return BuildCommand(requested_name, args)

        raise ValueError("Multiple matching commands found for {}"
                         .format(requested_command))

    @staticmethod
    def _get_implementations():
        return BuildCommand.__subclasses__()

    def execute(self, project_dir: str, dep_dir: str, compile_base_path: str) -> None:
        logger = logging.getLogger("buildcommand")

        command = self._get_command(self.args)
        output = Shell.exec(command, cwd=project_dir, logger=logger)

        self._copy_dependencies(output, dep_dir, compile_base_path)

    @staticmethod
    def name() -> str:
        raise NotImplementedError

    def _get_command(self, args: List[str]) -> str:
        return ' '.join([self._name] + args)

    def _copy_dependencies(self, output: str, dep_dir: str, compile_base_path: str) -> None:
        pass
