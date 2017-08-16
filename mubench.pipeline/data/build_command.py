import shutil
import os
import shlex
from glob import glob
from logging import Logger
from os import makedirs
from os.path import join, exists, dirname, splitext, relpath
from typing import List, Set

from utils.io import remove_tree, copy_tree
from utils.shell import Shell, CommandFailedError


class BuildCommand:
    def __init__(self, name: str, args: List[str]):
        self._name = name
        self.args = args

    @staticmethod
    def create(requested_command: str) -> 'BuildCommand':
        requested_command = shlex.split(requested_command)
        requested_name = requested_command[0]
        args = requested_command[1:]

        commands = BuildCommand._get_implementations()
        matching_commands = [c for c in commands if
                             c.name() == requested_name]
        if len(matching_commands) == 1:
            matching_command = matching_commands[0]
            return matching_command(requested_name, args)
        elif len(matching_commands) > 1:
            raise ValueError("Multiple matching commands found for {}"
                             .format(requested_command))
        else:
            return BuildCommand(requested_name, args)

    @staticmethod
    def _get_implementations():
        return BuildCommand.__subclasses__()

    def execute(self, project_dir: str, logger: Logger) -> Set[str]:
        command = self._get_command(self.args)

        try:
            output = Shell.exec(command, cwd=project_dir, logger=logger)
            return self._get_dependencies(output, project_dir, logger)
        except CommandFailedError as e:
            error_output = '\n' + self._get_errors(e.output, e.error)
            e.output = error_output
            e.error = ""
            raise

    @staticmethod
    def name() -> str:
        raise NotImplementedError

    def _get_command(self, args: List[str]) -> str:
        return ' '.join(shlex.quote(s) for s in [self._name] + self._prepare_args(args))

    def _prepare_args(self, args: List[str]) -> List[str]:
        return args

    def _get_errors(self, output: str, error: str) -> str:
        return output

    def _get_dependencies(self, shell_output: str, project_dir: str, logger: Logger) -> Set[str]:
        return []


class MavenCommand(BuildCommand):
    @staticmethod
    def name() -> str:
        return "mvn"

    def _prepare_args(self, args: List[str]) -> List[str]:
        return ["dependency:build-classpath", "-DincludeScope=compile"] + args

    def _get_errors(self, output: str, error: str) -> str:
        lines = output.splitlines()
        return '\n'.join([line for line in lines if line.startswith("[ERROR]")])

    def _get_dependencies(self, shell_output: str, project_dir: str, logger: Logger) -> Set[str]:
        # shell_output looks like (possibly multiple times, once for each Maven module):
        # [INFO] Dependencies classpath:
        # /path/dep1.jar:/path/dep2.jar

        classpath = set()
        lines = shell_output.splitlines()
        for line in [lines[i + 1].strip() for i, line in enumerate(lines) if "Dependencies classpath:" in line]:
            if line:
                classpath.update(line.split(":"))
        return classpath


class GradleCommand(BuildCommand):
    @staticmethod
    def name() -> str:
        return "gradle"

    def _prepare_args(self, args: List[str]) -> List[str]:
        return args + ["--debug"]

    def _get_errors(self, output: str, error: str) -> str:
        lines = output.splitlines()
        return '\n'.join([line for line in lines if "[ERROR]" in line])

    def _get_dependencies(self, shell_output: str, project_dir: str, logger: Logger) -> Set[str]:
        buildfile_dir = self._parse_buildfile_dir(self.args)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'classpath.gradle'), os.path.join(project_dir, buildfile_dir))
        command = "gradle :printClasspath -b '{}'".format(os.path.join(buildfile_dir, "classpath.gradle"))
        output = Shell.exec(command, cwd=project_dir, logger=logger)
        return self._parse_classpath(output)

    def _parse_classpath(self, shell_output: str) -> Set[str]:
        # shell_output looks like:
        # :printClasspath
        # /path/dependency1.jar
        # /path/dependency2.jar
        #
        # BUILD SUCCESSFUL

        lines = shell_output.splitlines()
        first_dependency_idx = next(i for i, line in enumerate(lines) if line == ":printClasspath") + 1
        first_empty_line_idx = next(i for i, line in enumerate(lines) if not line)
        return set(lines[first_dependency_idx:first_empty_line_idx])

    def _parse_buildfile_dir(self, args):
        buildfile_dir = ""

        if "-p" in args:
            buildfile_dir = args[args.index("-p") + 1]
        elif "--project-dir" in args:
            buildfile_dir = args[args.index("--project-dir") + 1]

        return buildfile_dir


class AntCommand(BuildCommand):
    @staticmethod
    def name() -> str:
        return "ant"

    def _prepare_args(self, args: List[str]) -> List[str]:
        return ["-debug", "-verbose"] + args

    def _get_errors(self, output: str, error: str) -> str:
        return error

    def _get_dependencies(self, shell_output: str, project_dir: str, logger: Logger) -> Set[str]:
        # shell_output looks like:
        #   [javac] '-classpath'
        #   [javac] '/project/build:/path/dep1.jar:/path/dep2.jar'

        classpath = set()
        lines = shell_output.splitlines()
        for line in [lines[i + 1] for i, line in enumerate(lines) if "[javac] '-classpath'" in line]:
            if line:
                classpath_start_idx = line.find("'") + 1
                classpath_end_idx = line.find("'", classpath_start_idx)
                classpath.update(line[classpath_start_idx:classpath_end_idx].split(":"))

        return classpath
