import logging
import shutil
from os import makedirs
from os.path import join, exists, isdir, dirname
from typing import List, Set

from benchmark.data.misuse import Misuse, Pattern
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import remove_tree, copy_tree
from benchmark.utils.shell import Shell, CommandFailedError


class Compile(DataReaderSubprocess):
    __BUILD_DIR = "build"

    def __init__(self, checkouts_base_path: str, compiles_base_path: str, pattern_frequency: int, force_compile):
        self.checkouts_base_path = checkouts_base_path
        self.compiles_base_path = compiles_base_path
        self.pattern_frequency = pattern_frequency
        self.force_compile = force_compile

    def run(self, misuse: Misuse):
        logger = logging.getLogger("compile")
        logger.info("Compiling project version...")
        logger.debug("- Force compile     = %r", self.force_compile)
        logger.debug("- Pattern frequency = %r", self.pattern_frequency)
        logger = logging.getLogger("compile.tasks")

        project_compile = misuse.get_compile(self.compiles_base_path)
        build_path = join(project_compile.base_path, Compile.__BUILD_DIR)
        build_config = misuse.build_config
        sources_path = join(build_path, build_config.src)
        classes_path = join(build_path, build_config.classes)

        needs_copy_sources = not isdir(project_compile.original_sources_path) or self.force_compile
        needs_copy_pattern_sources = not isdir(project_compile.pattern_sources_path) or self.force_compile
        needs_compile = not isdir(project_compile.original_classes_path) or self.force_compile
        needs_compile_patterns = not isdir(project_compile.pattern_classes_path) or self.force_compile

        if needs_copy_sources or needs_copy_pattern_sources or needs_compile or needs_compile_patterns:
            remove_tree(build_path)
            logger.debug("Copying to build directory...")
            checkout_path = misuse.get_checkout(self.checkouts_base_path).checkout_dir
            copy_tree(checkout_path, build_path)
            logger.debug("Copying additional resources...")
            self.__copy_additional_compile_sources(misuse, build_path)

        if not needs_copy_sources:
            logger.info("Already copied project source.")
        else:
            try:
                logger.info("Copying project sources...")
                self.__copy_original_sources(sources_path, project_compile.original_sources_path)
            except IOError as e:
                logger.error("Failed to copy project sources: %s", e)
                return DataReaderSubprocess.Answer.skip

        if not needs_copy_pattern_sources:
            logger.info("Already copied pattern sources.")
        else:
            try:
                logger.info("Copying pattern sources...")
                self.__copy_pattern_sources(misuse.patterns, project_compile.pattern_sources_path, self.pattern_frequency)
            except IOError as e:
                logger.error("Failed to copy pattern sources: %s", e)
                return DataReaderSubprocess.Answer.skip

        if not build_config.commands:
            logger.warn("Skipping compilation: not configured.")
            return DataReaderSubprocess.Answer.ok

        if not needs_compile:
            logger.info("Already compiled project.")
        else:
            try:
                logger.info("Compiling project...")
                self._compile(build_config.commands, build_path)

                logger.debug("Copying project classes...")
                copy_tree(classes_path, project_compile.original_classes_path)
            except CommandFailedError as e:
                logger.error("Compilation failed: %s", e)
                return DataReaderSubprocess.Answer.skip
            except FileNotFoundError as e:
                logger.error("Failed to copy classes: %s", e)
                return DataReaderSubprocess.Answer.skip

        if not misuse.patterns:
            logger.info("Skipping pattern compilation: no patterns.")
            return DataReaderSubprocess.Answer.ok

        if not needs_compile_patterns:
            logger.info("Already compiled patterns.")
        else:
            try:
                logger.debug("Copying patterns to source directory...")
                duplicates = self.__duplicate(misuse.patterns, sources_path, self.pattern_frequency)
                logger.info("Compiling patterns...")
                self._compile(build_config.commands, build_path)
                logger.debug("Copying pattern classes...")
                self.__copy(duplicates, classes_path, project_compile.pattern_classes_path)
            except CommandFailedError as e:
                logger.error("Compilation failed: %s", e)
                return DataReaderSubprocess.Answer.skip

        return DataReaderSubprocess.Answer.ok

    @staticmethod
    def __copy_original_sources(sources_path: str, destination: str):
        remove_tree(destination)
        makedirs(destination, exist_ok=True)
        copy_tree(sources_path, destination)

    @staticmethod
    def __copy_pattern_sources(patterns: Set[Pattern], destination: str, pattern_frequency: int):
        remove_tree(destination)
        for pattern in patterns:
            pattern.duplicate(destination, pattern_frequency)

    @staticmethod
    def __copy_additional_compile_sources(misuse, checkout_dir):
        additional_sources = misuse.additional_compile_sources
        if exists(additional_sources):
            copy_tree(additional_sources, checkout_dir)

    @staticmethod
    def _compile(commands: List[str], project_dir: str) -> None:
        logger = logging.getLogger("compile.tasks.exec")
        for command in commands:
            Shell.exec(command, cwd=project_dir, logger=logger)

    @staticmethod
    def __duplicate(patterns, destination, pattern_frequency: int):
        duplicates = set()
        for pattern in patterns:
            duplicates.update(pattern.duplicate(destination, pattern_frequency))
        return duplicates

    @staticmethod
    def __copy(patterns, classes_path, destination):
        for pattern in patterns:
            pattern_class_file_name = pattern.file_name + ".class"
            new_name = join(destination, pattern_class_file_name)
            makedirs(dirname(new_name), exist_ok=True)
            shutil.copy(join(classes_path, pattern_class_file_name), new_name)
