import logging
import shutil
import os
import shlex
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
            logger.debug("Copying checkout to build directory...")
            checkout_path = version.get_checkout(self.checkouts_base_path).checkout_dir
            self.__clean_copy(checkout_path, build_path)
            logger.debug("Copying additional resources...")
            self.__copy_additional_compile_sources(version, build_path)

        if not needs_copy_sources:
            logger.debug("Already copied source.")
        else:
            try:
                logger.info("Copying sources...")
                logger.debug("Copying project sources...")
                self.__clean_copy(sources_path, project_compile.original_sources_path)
                logger.debug("Copying misuse sources...")
                self.__copy_misuse_sources(sources_path, version.misuses, project_compile.misuse_source_path)
                logger.info("Copying pattern sources...")
                self.__copy_pattern_sources(version.misuses, project_compile)
            except IOError as e:
                remove_tree(project_compile.original_sources_path)
                remove_tree(project_compile.misuse_source_path)
                remove_tree(project_compile.pattern_sources_base_path)
                logger.error("Failed to copy sources: %s", e)
                return self.skip(version)

        if not version.compile_commands:
            logger.warning("Skipping compilation: not configured.")
            return self.skip(version)

        if not needs_compile:
            logger.debug("Already compiled project.")
        else:
            try:
                logger.info("Compiling project...")
                logger.debug("Copying patterns to source directory...")
                self.__copy(version.patterns, sources_path)
                self._compile(version.compile_commands, build_path, project_compile.dependencies_path)
                logger.debug("Move pattern classes...")
                self.__copy_pattern_classes(version.misuses, classes_path, project_compile)
                self.__remove_patter_classes(version.misuses, classes_path)
                logger.debug("Copy project classes...")
                self.__clean_copy(classes_path, project_compile.original_classes_path)
                logger.debug("Create project jar...")
                self.__create_jar(project_compile.original_classes_path, project_compile.original_classpath)
                logger.debug("Copy misuse classes...")
                self.__copy_misuse_classes(classes_path, version.misuses, project_compile.misuse_classes_path)
            except Exception as e:
                logger.error("Compilation failed: %s", e)
                remove_tree(project_compile.pattern_classes_base_path)
                remove_tree(project_compile.original_classpath)
                remove_tree(project_compile.original_classpath)
                remove_tree(project_compile.misuse_classes_path)
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
                command = "mvn dependency:build-classpath -DincludeScope=compile " + command[4:]
                output = Shell.exec(command, cwd=project_dir, logger=logger)
                dependencies = Compile.__parse_maven_classpath(output)
                Compile._copy_classpath(dependencies, dep_dir)
            elif command.startswith("ant"):
                command += " -debug -verbose"
                output = Shell.exec(command, cwd=project_dir, logger=logger)
                dependencies = Compile.__parse_ant_classpath(output)
                Compile._copy_classpath(dependencies, dep_dir)
            elif command.startswith("gradle "):
                Shell.exec(command, cwd=project_dir, logger=logger)
                buildfile_dir = Compile.__parse_buildfile_dir(command)
                shutil.copy(os.path.join(os.path.dirname(__file__), 'classpath.gradle'), os.path.join(project_dir, buildfile_dir))
                command = "gradle :printClasspath -b '{}'".format(os.path.join(buildfile_dir, "classpath.gradle"))
                output = Shell.exec(command, cwd=project_dir, logger=logger)
                dependencies = Compile.__parse_gradle_classpath(output)
                Compile._copy_classpath(dependencies, dep_dir)
            else:
                Shell.exec(command, cwd=project_dir, logger=logger)

    @staticmethod
    def __parse_buildfile_dir(command):
        args = shlex.split(command)
        buildfile_dir = ""

        if "-p" in args:
            buildfile_dir = args[args.index("-p")+1]
        elif "--project-dir" in args:
            buildfile_dir = args[args.index("--project-dir") + 1]

        return buildfile_dir

    @staticmethod
    def __parse_maven_classpath(shell_output: str) -> List[str]:
        # shell_output looks like (possibly multiple times, once for each Maven module):
        # [INFO] Dependencies classpath:
        # /path/dep1.jar:/path/dep2.jar

        classpath = []
        lines = shell_output.splitlines()
        for line in [lines[i + 1].strip() for i, line in enumerate(lines) if "Dependencies classpath:" in line]:
            if line:
                classpath.extend(line.split(":"))

        return classpath

    @staticmethod
    def __parse_ant_classpath(shell_output: str) -> List[str]:
        # shell_output looks like:
        #   [javac] '-classpath'
        #   [javac] '/project/build:/path/dep1.jar:/path/dep2.jar'

        classpath_preamble = "[javac] '-classpath'"
        classpath_preamble_end_idx = shell_output.find(classpath_preamble) + len(classpath_preamble)
        classpath_start_idx = shell_output.find("'", classpath_preamble_end_idx) + 1
        classpath_end_idx = shell_output.find("'", classpath_start_idx)
        classpath = shell_output[classpath_start_idx:classpath_end_idx]
        return classpath.split(":")

    @staticmethod
    def __parse_gradle_classpath(shell_output: str) -> List[str]:
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
        makedirs(dep_dir, exist_ok=True)
        for dependency in dependencies:
            if not os.path.isdir(dependency):
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

    @staticmethod
    def __remove_patter_classes(misuses: List[Misuse], classes_path: str):
        for misuse in misuses:
            for pattern in misuse.patterns:
                pattern_class_file_name = pattern.relative_path_without_extension + ".class"
                try:
                    os.remove(join(classes_path, pattern_class_file_name))
                except OSError:
                    pass

    @staticmethod
    def __create_jar(classes_path, jar_path):
        zip_path = shutil.make_archive(jar_path, 'zip', classes_path)
        os.rename(zip_path, jar_path)
