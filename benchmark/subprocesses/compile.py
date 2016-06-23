import logging
import shutil
from os import makedirs
from os.path import join, exists, isdir, dirname
from typing import List, Set

from benchmark.data.misuse import Misuse, Pattern
from benchmark.data.project_compile import ProjectCompile
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import remove_tree, copy_tree
from benchmark.utils.shell import Shell, CommandFailedError


class Compile(DataReaderSubprocess):
    __BUILD_DIR = "build"

    def __init__(self, checkout_base_dir: str, pattern_frequency: int, force_compile):
        self.checkout_base_dir = checkout_base_dir
        self.pattern_frequency = pattern_frequency
        self.force_compile = force_compile

    def run(self, misuse: Misuse):
        logger = logging.getLogger("compile")
        logger.info("Compiling project version...")
        logger.debug("- Force compile     = %r", self.force_compile)
        logger.debug("- Pattern frequency = %r", self.pattern_frequency)
        logger = logging.getLogger("compile.tasks")

        build_config = misuse.build_config

        checkout = misuse.get_checkout(self.checkout_base_dir)
        checkout_dir = checkout.checkout_dir
        base_path = dirname(checkout_dir)

        build_path = join(base_path, Compile.__BUILD_DIR)
        sources_path = join(build_path, build_config.src)
        classes_path = join(build_path, build_config.classes)

        compile = ProjectCompile(base_path)

        logger.debug("Copying to build directory...")
        copy_tree(checkout_dir, build_path)
        logger.debug("Copying additional resources...")
        self.__copy_additional_compile_sources(misuse, build_path)

        if isdir(compile.original_sources_path) and not self.force_compile:
            logger.info("Already copied project source.")
        else:
            try:
                logger.info("Copying project sources...")
                self.__copy_original_sources(sources_path, compile.original_sources_path)
            except IOError as e:
                logger.error("Failed to copy project sources: %s", e)
                return DataReaderSubprocess.Answer.skip

        if isdir(compile.pattern_sources_path) and not self.force_compile:
            logger.info("Already copied pattern sources.")
        else:
            try:
                logger.info("Copying pattern sources...")
                self.__copy_pattern_sources(misuse.patterns, compile.pattern_sources_path, self.pattern_frequency)
            except IOError as e:
                logger.error("Failed to copy pattern sources: %s", e)
                return DataReaderSubprocess.Answer.skip

        if not build_config.commands:
            logger.warn("Skipping compilation: not configured.")
            return DataReaderSubprocess.Answer.ok

        if isdir(compile.original_classes_path) and not self.force_compile:
            logger.info("Already compiled project.")
        else:
            try:
                logger.info("Compiling project...")
                self._compile(build_config.commands, build_path)

                logger.debug("Copying project classes...")
                copy_tree(classes_path, compile.original_classes_path)
            except CommandFailedError as e:
                logger.error("Compilation failed: %s", e)
                return DataReaderSubprocess.Answer.skip

        if not misuse.patterns:
            logger.info("Skipping pattern compilation: no patterns.")
            return DataReaderSubprocess.Answer.ok

        if isdir(compile.pattern_classes_path) and not self.force_compile:
            logger.info("Already compiled patterns.")
        else:
            try:
                logger.debug("Copying patterns to source directory...")
                duplicates = self.__duplicate(misuse.patterns, sources_path, self.pattern_frequency)
                logger.info("Compiling patterns...")
                self._compile(build_config.commands, build_path)
                logger.debug("Copying pattern classes...")
                self.__copy(duplicates, classes_path, compile.pattern_classes_path)
            except CommandFailedError as e:
                logger.error("Compilation failed: %s", e)
                return DataReaderSubprocess.Answer.skip

        return DataReaderSubprocess.Answer.ok

    @staticmethod
    def __copy_original_sources(sources_path: str, destination: str):
        remove_tree(destination)
        makedirs(destination, exist_ok=True)
        print("copy {}\n     {}".format(sources_path, destination))
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
