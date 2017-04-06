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
                output = Shell.exec(command, cwd=project_dir,logger=logger)
                dependencies = Compile._parse_maven_classpath(output)
                Compile._copy_classpath(dependencies, dep_dir)
            elif command.startswith("ant "):
                command += " -debug -verbose"
                output = Shell.exec(command, cwd=project_dir,logger=logger)
                dependencies = Compile._parse_ant_classpath(output)
                Compile._copy_classpath(dependencies, dep_dir)
            elif command.startswith("gradle "):
                Shell.exec(command,cwd=project_dir,logger=logger)
                shutil.copy(os.path.dirname(__file__) + '/classpath.gradle', project_dir)
                output = Shell.exec("gradle :printClasspath -b classpath.gradle", cwd=project_dir, logger=logger)
                dependencies = Compile._parse_gradle_classpath(output)
                Compile._copy_classpath(dependencies, dep_dir)
            else:
                Shell.exec(command, cwd=project_dir, logger=logger)

    @staticmethod
    def _parse_maven_classpath(shell_output: str) -> List[str]:
        search_str = "Dependencies classpath:\n"
        offset = len(search_str)
        start_idx = shell_output.find(search_str)
        end_idx = shell_output.find("[INFO]", start_idx)
        classpath = shell_output[start_idx + offset:end_idx]
        if "\n" in classpath:
            classpath = classpath.replace("\n", "")
        return classpath.split(":")

    @staticmethod
    def _parse_ant_classpath(shell_output: str) -> List[str]:
        start_str = "[javac] '-classpath'\n"
        end_str = "[javac] '"
        offset_start = len(start_str)
        offset_end = len(end_str)
        start_idx = shell_output.find(start_str)
        line_idx = shell_output.find(end_str, start_idx + offset_start)
        line_end_idx = shell_output.find("'\n", line_idx+offset_end)+2
        classpath = shell_output[line_idx+offset_end:line_end_idx]
        filtered_deps = []
        for dep in classpath.split(":"):
            if "'\n" in dep:
                dep = dep[:2]
            if ".jar" in dep:
                filtered_deps.append(dep)
        return filtered_deps

    @staticmethod
    def _parse_gradle_classpath(shell_output: str) -> List[str]:
        start_idx = shell_output.find("\n")
        end_idx = shell_output.find("\n\nB", start_idx)
        classpath = shell_output[start_idx+1:end_idx]
        return classpath.split("\n")

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
