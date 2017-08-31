import logging
import shutil
import os
import shlex
from glob import glob
from logging import Logger
from os import makedirs
from os.path import join, exists, dirname, splitext, relpath
from tempfile import mkdtemp
from typing import List, Set

from data.build_command import BuildCommand
from data.misuse import Pattern, Misuse
from data.project import Project
from data.project_compile import ProjectCompile
from data.project_version import ProjectVersion
from tasks.project_version_task import ProjectVersionTask
from utils.io import remove_tree, copy_tree
from utils.shell import Shell, CommandFailedError


class Compile(ProjectVersionTask):
    __BUILD_DIR = "build"

    def __init__(self, checkouts_base_path: str, compiles_base_path: str,
                 force_compile: bool, use_temp_dir: bool):
        super().__init__()
        self.checkouts_base_path = checkouts_base_path
        self.compiles_base_path = compiles_base_path
        self.force_compile = force_compile
        self.use_temp_dir = use_temp_dir

    def process_project_version(self, project: Project, version: ProjectVersion):
        logger = logging.getLogger("compile")
        logger.info("Compiling %s...", version)
        logger = logging.getLogger("compile.tasks")

        project_compile = version.get_compile(self.compiles_base_path)

        build_path = mkdtemp(prefix='mubench-compile_') if self.use_temp_dir \
                     else join(project_compile.base_path, Compile.__BUILD_DIR)

        sources_path = join(build_path, version.source_dir)
        classes_path = join(build_path, version.classes_dir)

        if self.force_compile:
            logger.debug("Force compile - removing previous compiles...")
            project_compile.delete()

        try:
            needs_copy_sources = project_compile.needs_copy_sources()
            needs_compile = project_compile.needs_compile()

            if needs_copy_sources or needs_compile:
                logger.debug("Copying checkout to build directory...")
                checkout_path = version.get_checkout(self.checkouts_base_path).checkout_dir
                copy_tree(checkout_path, build_path)
                logger.debug("Copying additional resources...")
                self.__copy_additional_compile_sources(version, build_path)

            if not needs_copy_sources:
                logger.debug("Already copied source.")
            else:
                logger.info("Copying sources...")
                logger.debug("Copying project sources...")
                copy_tree(sources_path, project_compile.original_sources_path)
                logger.debug("Copying misuse sources...")
                self.__copy_misuse_sources(sources_path, version.misuses, project_compile.misuse_source_path)
                logger.info("Copying pattern sources...")
                self.__copy_pattern_sources(version.misuses, project_compile)

            if not version.compile_commands:
                logger.warning("Skipping compilation: not configured.")
                return self.skip(version)

            if not needs_compile:
                logger.debug("Already compiled project.")
            else:
                logger.info("Compiling project...")
                logger.debug("Copying patterns to source directory...")
                self.__copy(version.patterns, sources_path)
                self._compile(version.compile_commands,
                              build_path,
                              project_compile.dependencies_path,
                              self.compiles_base_path,
                              logger)
                logger.debug("Move pattern classes...")
                self.__copy_pattern_classes(version.misuses, classes_path, project_compile)
                self.__remove_pattern_classes(version.misuses, classes_path)
                logger.debug("Copy project classes...")
                copy_tree(classes_path, project_compile.original_classes_path)
                logger.debug("Create project jar...")
                self.__create_jar(project_compile.original_classes_path, project_compile.original_classpath)
                logger.debug("Copy misuse classes...")
                self.__copy_misuse_classes(classes_path, version.misuses, project_compile.misuse_classes_path)

            if self.use_temp_dir:
                logger.debug("Moving complete build to persistent directory...")
                copy_tree(build_path, join(project_compile.base_path, Compile.__BUILD_DIR))
                remove_tree(build_path)
        except Exception as e:
            logger.error("Compilation failed: %s", e)
            project_compile.delete()
            return self.skip(version)

        return self.ok()

    @staticmethod
    def __copy_misuse_sources(sources_path, misuses, destination):
        for misuse in misuses:
            file = misuse.location.file
            dst = join(destination, file)
            makedirs(dirname(dst), exist_ok=True)
            shutil.copy(join(sources_path, file), dst)

    @staticmethod
    def __copy_pattern_sources(misuses: List[Misuse], project_compile: ProjectCompile):
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
    def _compile(commands: List[str], project_dir: str, dep_dir: str,
                 compile_base_path: str, logger: Logger) -> None:
        for command in commands:
            dependencies = BuildCommand.create(command).execute(project_dir, logger)
            Compile.__copy_dependencies(dependencies, dep_dir, compile_base_path)

    @staticmethod
    def __copy_misuse_classes(classes_path, misuses, destination):
        for misuse in misuses:
            basepath = join(classes_path, splitext(misuse.location.file)[0])
            classes = glob(basepath + ".class") + glob(basepath + "$*.class")
            for class_ in classes:
                dst = join(destination, relpath(class_, classes_path))
                makedirs(dirname(dst), exist_ok=True)
                shutil.copy(class_, dst)

    @staticmethod
    def __copy(patterns: Set[Pattern], destination: str):
        for pattern in patterns:
            pattern.copy(destination)

    @staticmethod
    def __copy_pattern_classes(misuses: List[Misuse], classes_path: str, project_compile: ProjectCompile):
        for misuse in misuses:
            pattern_classes_path = project_compile.get_pattern_classes_path(misuse)
            for pattern in misuse.patterns:
                pattern_class_file_name = pattern.relative_path_without_extension + ".class"
                new_name = join(pattern_classes_path, pattern_class_file_name)
                makedirs(dirname(new_name), exist_ok=True)
                shutil.copy(join(classes_path, pattern_class_file_name), new_name)

    @staticmethod
    def __remove_pattern_classes(misuses: List[Misuse], classes_path: str):
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

    @staticmethod
    def __copy_dependencies(dependencies: Set[str], dep_dir: str, compile_base_path: str):
        makedirs(dep_dir, exist_ok=True)
        for dependency in dependencies:
            if os.path.isdir(dependency):
                # dependency is a classes directory
                dep_name = os.path.relpath(dependency, compile_base_path)
                dep_name = dep_name.replace(os.sep, '-')
                Compile.__create_jar(dependency, os.path.join(dep_dir, dep_name + ".jar"))
            else:
                shutil.copy(dependency, dep_dir)
