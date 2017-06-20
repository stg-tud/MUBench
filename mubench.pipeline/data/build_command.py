import logging
import shutil
import os
import shlex
from glob import glob
from os import makedirs
from os.path import join, exists, dirname, splitext, relpath
from typing import List, Set

from utils.io import remove_tree, copy_tree
from utils.shell import Shell, CommandFailedError


class BuildCommand:
    def __init__(self, name: str, args: List[str]):
        self.logger = logging.getLogger("buildcommand")
        self._name = name
        self.args = args

    @staticmethod
    def get(requested_command: str) -> 'BuildCommand':
        requested_command = shlex.split(requested_command)
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
        command = self._get_command(self.args)
        output = Shell.exec(command, cwd=project_dir, logger=self.logger)

        self._copy_dependencies(output, project_dir, dep_dir, compile_base_path)

    @staticmethod
    def name() -> str:
        raise NotImplementedError

    def _get_command(self, args: List[str]) -> str:
        return ' '.join([self._name] + self._extend_args(args))

    def _extend_args(self, args: List[str]) -> List[str]:
        return args

    def _copy_dependencies(self, exec_output: str, project_dir: str, dep_dir: str, compile_base_path: str) -> None:
        pass


class MavenCommand(BuildCommand):
    @staticmethod
    def name() -> str:
        return "mvn"

    def _extend_args(self, args: List[str]) -> List[str]:
        return ["dependency:build-classpath", "-DincludeScope=compile"] + args

    def _copy_dependencies(self, exec_output: str, project_dir: str, dep_dir: str, compile_base_path: str) -> None:
        dependencies = MavenCommand.__parse_maven_classpath(exec_output)
        _copy_classpath(dependencies, dep_dir, compile_base_path)

    @staticmethod
    def __parse_maven_classpath(shell_output: str) -> Set[str]:
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

    def _copy_dependencies(self, exec_output: str, project_dir: str,
                           dep_dir: str, compile_base_path: str) -> None:
        buildfile_dir = GradleCommand.__parse_buildfile_dir(self.args)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'classpath.gradle'), os.path.join(project_dir, buildfile_dir))
        command = "gradle :printClasspath -b '{}'".format(os.path.join(buildfile_dir, "classpath.gradle"))
        output = Shell.exec(command, cwd=project_dir, logger=self.logger)
        dependencies = GradleCommand.__parse_gradle_classpath(output)
        _copy_classpath(dependencies, dep_dir, compile_base_path)

    @staticmethod
    def __parse_gradle_classpath(shell_output: str) -> Set[str]:
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

    @staticmethod
    def __parse_buildfile_dir(args):
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

    def _extend_args(self, args: List[str]) -> List[str]:
        return ["-debug", "-verbose"] + args

    def _copy_dependencies(self, exec_output: str, project_dir: str,
                           dep_dir: str, compile_base_path: str) -> None:
        dependencies = AntCommand.__parse_ant_classpath(exec_output)
        _copy_classpath(dependencies, dep_dir, compile_base_path)

    @staticmethod
    def __parse_ant_classpath(shell_output: str) -> Set[str]:
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


def _copy_classpath(dependencies: Set[str], dep_dir: str, compile_base_path: str):
    remove_tree(dep_dir)
    makedirs(dep_dir, exist_ok=True)
    for dependency in dependencies:
        if os.path.isdir(dependency):
            # dependency is a classes directory
            dep_name = os.path.relpath(dependency, compile_base_path)
            dep_name = dep_name.replace(os.sep, '-')
            _create_jar(dependency, os.path.join(dep_dir, dep_name + ".jar"))
        else:
            shutil.copy(dependency, dep_dir)

def __create_jar(classes_path, jar_path):
    zip_path = shutil.make_archive(jar_path, 'zip', classes_path)
    os.rename(zip_path, jar_path)
