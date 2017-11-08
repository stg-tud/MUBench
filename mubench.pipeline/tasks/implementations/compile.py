import logging
import os
import shutil
from logging import Logger
from os import makedirs
from os.path import join, exists
from tempfile import mkdtemp
from typing import List, Set

from data.build_command import BuildCommand
from data.project_checkout import ProjectCheckout
from data.project_version import ProjectVersion
from utils.io import remove_tree, copy_tree


class CompileTask:
    def __init__(self, compiles_base_path: str, force_compile: bool, use_temp_dir: bool):
        super().__init__()
        self.compiles_base_path = compiles_base_path
        self.force_compile = force_compile
        self.use_temp_dir = use_temp_dir

    def run(self, version: ProjectVersion, checkout: ProjectCheckout):
        logger = logging.getLogger("task.compile")
        logger.info("Compiling %s...", version)

        project_compile = version.get_compile(self.compiles_base_path)

        build_path = mkdtemp(prefix='mubench-compile_') if self.use_temp_dir else project_compile.build_dir

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
                checkout_path = checkout.checkout_dir
                copy_tree(checkout_path, build_path)
                logger.debug("Copying additional resources...")
                self.__copy_additional_compile_sources(version, build_path)

            if not needs_copy_sources:
                logger.debug("Already copied source.")
            else:
                logger.info("Copying sources...")
                logger.debug("Copying project sources...")
                copy_tree(sources_path, project_compile.original_sources_path)

            if not version.compile_commands:
                raise UserWarning("Skipping compilation: not configured.")

            if not needs_compile:
                logger.debug("Already compiled project.")
            else:
                logger.info("Compiling project...")
                self._compile(version.compile_commands,
                              build_path,
                              project_compile.dependencies_path,
                              self.compiles_base_path,
                              logger)
                logger.debug("Copy project classes...")
                copy_tree(classes_path, project_compile.original_classes_path)
                logger.debug("Create project jar...")
                self.__create_jar(project_compile.original_classes_path, project_compile.original_classpath)

            if self.use_temp_dir:
                logger.debug("Moving complete build to persistent directory...")
                copy_tree(build_path, project_compile.build_dir)
                remove_tree(build_path)
        except Exception:
            project_compile.delete()
            raise

        return project_compile

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
            CompileTask.__copy_dependencies(dependencies, dep_dir, compile_base_path)

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
                CompileTask.__create_jar(dependency, os.path.join(dep_dir, dep_name + ".jar"))
            else:
                shutil.copy(dependency, dep_dir)
