import logging
import shutil
import os
from glob import glob
from os import makedirs
from os.path import join, exists, dirname, splitext, relpath
from typing import List, Set

from data.misuse import Pattern, Misuse
from data.project import Project
from data.project_compile import ProjectCompile
from data.project_version import ProjectVersion
from requirements import JavaRequirement, MavenRequirement, GradleRequirement
from tasks.project_version_task import ProjectVersionTask
from utils.io import remove_tree, copy_tree
from utils.shell import Shell, CommandFailedError


class Compile(ProjectVersionTask):
    __BUILD_DIR = "build"

    def __init__(self, checkouts_base_path: str, compiles_base_path: str, force_compile):
        super().__init__()
        self.checkouts_base_path = checkouts_base_path
        self.compiles_base_path = compiles_base_path
        self.force_compile = force_compile

    def get_requirements(self):
        return [JavaRequirement(), MavenRequirement(), GradleRequirement()]

    def process_project_version(self, project: Project, version: ProjectVersion):
        logger = logging.getLogger("compile")
        logger.info("Compiling %s...", version)
        logger.debug("- Force compile     = %r", self.force_compile)
        logger = logging.getLogger("compile.tasks")

        project_compile = version.get_compile(self.compiles_base_path)
        build_path = join(project_compile.base_path, Compile.__BUILD_DIR)
        sources_path = join(build_path, version.source_dir)
        classes_path = join(build_path, version.classes_dir)

        needs_copy_sources = project_compile.needs_copy_sources() or self.force_compile
        needs_compile = project_compile.needs_compile() or self.force_compile

        if needs_copy_sources or needs_compile:
            logger.debug("Copying to build directory...")
            checkout_path = version.get_checkout(self.checkouts_base_path).checkout_dir
            self.__clean_copy(checkout_path, build_path)
            logger.debug("Copying additional resources...")
            self.__copy_additional_compile_sources(version, build_path)

        if not needs_copy_sources:
            logger.debug("Already copied project source.")
        else:
            try:
                logger.info("Copying project sources...")
                self.__clean_copy(sources_path, project_compile.original_sources_path)
                self.__copy_misuse_sources(sources_path, version.misuses, project_compile.misuse_source_path)
            except IOError as e:
                logger.error("Failed to copy project sources: %s", e)
                return self.skip(version)

        if not version.compile_commands:
            logger.warn("Skipping compilation: not configured.")
            return self.skip(version)

        if not needs_compile:
            logger.info("Already compiled project.")
        else:
            try:
                logger.info("Compiling project...")
                self._compile(version.compile_commands, build_path, project_compile.dependencies_path)
                logger.debug("Copying project classes...")
                self.__clean_copy(classes_path, project_compile.original_classes_path)
                self.__copy_misuse_classes(classes_path, version.misuses, project_compile.misuse_classes_path)
            except CommandFailedError as e:
                logger.error("Compilation failed: %s", e)
                return self.skip(version)
            except FileNotFoundError as e:
                logger.error("Failed to copy classes: %s", e)
                return self.skip(version)

        if not version.patterns:
            logger.info("Skipping pattern compilation: no patterns.")
            return self.ok()

        needs_copy_pattern_sources = project_compile.needs_copy_pattern_sources() or self.force_compile
        needs_compile_patterns = project_compile.needs_compile_patterns() or self.force_compile

        if needs_copy_pattern_sources or needs_compile_patterns:
            logger.debug("Copying to build directory...")
            checkout_path = version.get_checkout(self.checkouts_base_path).checkout_dir
            self.__clean_copy(checkout_path, build_path)
            logger.debug("Copying additional resources...")
            self.__copy_additional_compile_sources(version, build_path)

        if not needs_copy_pattern_sources:
            logger.debug("Already copied pattern sources.")
        else:
            try:
                logger.info("Copying pattern sources...")
                self.__copy_pattern_sources(version.misuses, project_compile)
            except IOError as e:
                logger.error("Failed to copy pattern sources: %s", e)
                return self.skip(version)

        if not needs_compile_patterns:
            logger.info("Already compiled patterns.")
        else:
            try:
                logger.debug("Copying patterns to source directory...")
                self.__copy(version.patterns, sources_path)
                logger.info("Compiling patterns...")
                self._compile(version.compile_commands, build_path, project_compile.dependencies_path)
                logger.debug("Copying pattern classes...")
                self.__copy_pattern_classes(version.misuses, classes_path, project_compile)
            except FileNotFoundError as e:
                remove_tree(project_compile.pattern_classes_base_path)
                logger.error("Compilation failed: %s", e)
                return self.skip(version)
            except CommandFailedError as e:
                logger.error("Compilation failed: %s", e)
                return self.skip(version)

        return self.ok()

    @staticmethod
    def __clean_copy(sources_path: str, destination: str):
        remove_tree(destination)
        copy_tree(sources_path, destination)

    @staticmethod
    def __copy_misuse_sources(sources_path, misuses, destination):
        remove_tree(destination)
        for misuse in misuses:
            file = misuse.location.file
            dst = join(destination, file)
            makedirs(dirname(dst), exist_ok=True)
            shutil.copy(join(sources_path, file), dst)

    @staticmethod
    def __copy_pattern_sources(misuses: List[Misuse], project_compile: ProjectCompile):
        remove_tree(project_compile.pattern_sources_base_path)
        for misuse in misuses:
            pattern_source_path = project_compile.get_pattern_source_path(misuse)
            for pattern in misuse.patterns:
                pattern.copy(pattern_source_path)

    @staticmethod
    def __copy_additional_compile_sources(version: ProjectVersion, checkout_dir: str):
        additional_sources = version.additional_compile_sources
        if exists(additional_sources):
            copy_tree(additional_sources, checkout_dir)

    @staticmethod
    def _compile(commands: List[str], project_dir: str, dep_dir: str) -> None:
        logger = logging.getLogger("compile.tasks.exec")
        for command in commands:
            if command.startswith("mvn "):
                command = "mvn dependency:build-classpath " + command[4:]
                output = Shell.exec(command, cwd=project_dir, logger=logger)
                dependencies = Compile._parse_maven_classpath(output)
                Compile._copy_classpath(dependencies, dep_dir)
            elif command.startswith("ant"):
                command += " -debug -verbose"
                output = Shell.exec(command, cwd=project_dir, logger=logger)
                dependencies = Compile._parse_ant_classpath(output)
                Compile._copy_classpath(dependencies, dep_dir)
            elif command.startswith("gradle "):
                Shell.exec(command, cwd=project_dir, logger=logger)
                buildfile_dir, classpath_cmd = Compile._parse_buildfile_dir(command)
                shutil.copy(os.path.dirname(__file__) + '/classpath.gradle', project_dir + "/" + buildfile_dir)
                output = Shell.exec(classpath_cmd, cwd=project_dir, logger=logger)
                dependencies = Compile._parse_gradle_classpath(output)
                Compile._copy_classpath(dependencies, dep_dir)
            else:
                Shell.exec(command, cwd=project_dir, logger=logger)

    @staticmethod
    def _parse_buildfile_dir(command):
        # parsing for "-p" or "--project-dir" in gradle command
        # and adjusting printClasspath command with it
        # gradle :printClasspath -b buildfile_dir/classpath.gradle

        args = command.split()
        buildfile_dir = ""
        if "-p" in args or "--project-dir" in args:
            # dir is one index behind "-p" or "--project-dir" in args
            last_index = 0
            if "--project-dir" in args:
                last_index = args.index("--project-dir") + 1
            else:
                last_index = args.index("-p") + 1
            buildfile_dir += args[last_index]

            # add rest of dir name if not even amount of " or ' in dir name (dirs with spaces are wrapped)
            while buildfile_dir.count('"') % 2 is not 0 or buildfile_dir.count('\'') % 2 is not 0:
                last_index += 1
                buildfile_dir += " " + args[last_index]

        # remove ' or " and add / if missing
        buildfile_dir = buildfile_dir.replace("'", "")
        buildfile_dir = buildfile_dir.replace("\"", "")
        if buildfile_dir is not "" and not buildfile_dir.endswith("/"):
            buildfile_dir += "/"

        cmd = "gradle :printClasspath -b '" + buildfile_dir + "classpath.gradle'"
        return buildfile_dir, cmd

    @staticmethod
    def _parse_maven_classpath(shell_output: str) -> List[str]:
        # shell_output looks like:
        # [INFO] Dependencies classpath:
        # /path/dep1.jar:/path/dep2.jar

        classpath_preamble = "Dependencies classpath:"
        classpath_start_idx = shell_output.find(classpath_preamble) + len(classpath_preamble)
        classpath_end_idx = shell_output.find("[INFO]", classpath_start_idx)
        classpath = shell_output[classpath_start_idx:classpath_end_idx].strip()
        return classpath.split(":")

    @staticmethod
    def _parse_ant_classpath(shell_output: str) -> List[str]:
        # shell_output looks like:
        #   [javac] '-classpath'
        #   [javac] '/project/build:/path/dep1.jar:/path/dep2.jar'

        classpath_preamble = "[javac] '-classpath'"
        classpath_preamble_end_idx = shell_output.find(classpath_preamble) + len(classpath_preamble)
        classpath_start_idx = shell_output.find("'", classpath_preamble_end_idx) + 1
        classpath_end_idx = shell_output.find("'", classpath_start_idx)
        classpath = shell_output[classpath_start_idx:classpath_end_idx]
        return classpath.split(":")[1:]

    @staticmethod
    def _parse_gradle_classpath(shell_output: str) -> List[str]:
        # shell_output looks like:
        # :printClasspath
        # /path/dependency1.jar
        # /path/dependency2.jar
        #
        # BUILD SUCCESSFUL

        lines = shell_output.splitlines()
        first_dependency_idx = next(i for i, line in enumerate(lines) if line == ":printClasspath") + 1
        first_empty_line_idx = next(i for i, line in enumerate(lines) if not line)
        return lines[first_dependency_idx:first_empty_line_idx]

    @staticmethod
    def _copy_classpath(dependencies: List[str], dep_dir: str):
        remove_tree(dep_dir)
        makedirs(dirname(dep_dir + "/"), exist_ok=True)
        for dependency in dependencies:
            shutil.copy(dependency, dep_dir)

    @staticmethod
    def __copy_misuse_classes(classes_path, misuses, destination):
        remove_tree(destination)
        for misuse in misuses:
            basepath = join(classes_path, splitext(misuse.location.file)[0])
            classes = glob(basepath + ".class") + glob(basepath + "$*.class")
            for clazz in classes:
                dst = join(destination, relpath(clazz, classes_path))
                makedirs(dirname(dst), exist_ok=True)
                shutil.copy(clazz, dst)

    @staticmethod
    def __copy(patterns: Set[Pattern], destination: str):
        for pattern in patterns:
            pattern.copy(destination)

    @staticmethod
    def __copy_pattern_classes(misuses: List[Misuse], classes_path: str, project_compile: ProjectCompile):
        remove_tree(project_compile.pattern_classes_base_path)
        for misuse in misuses:
            pattern_classes_path = project_compile.get_pattern_classes_path(misuse)
            for pattern in misuse.patterns:
                pattern_class_file_name = pattern.relative_path_without_extension + ".class"
                new_name = join(pattern_classes_path, pattern_class_file_name)
                makedirs(dirname(new_name), exist_ok=True)
                shutil.copy(join(classes_path, pattern_class_file_name), new_name)
