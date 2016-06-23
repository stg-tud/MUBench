import logging
import os
import shutil
import subprocess
from os import makedirs
from os.path import join, exists, isdir, dirname, isfile

from typing import List

from benchmark.data.misuse import Misuse
from benchmark.data.project_compile import ProjectCompile
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import remove_tree, copy_tree
from benchmark.utils.printing import subprocess_print, print_ok
from benchmark.utils.shell import Shell, CommandFailedError


class Compile(DataReaderSubprocess):
    __BUILD_DIR = "build"

    def __init__(self, checkout_base_dir: str, src_normal: str, classes_normal: str,
                 src_patterns: str, classes_patterns: str, pattern_frequency: int, outlog: str, errlog: str):
        self.checkout_base_dir = checkout_base_dir
        self.src_normal = src_normal
        self.classes_normal = classes_normal
        self.src_patterns = src_patterns
        self.classes_patterns = classes_patterns
        self.pattern_frequency = pattern_frequency
        self.outlog = outlog
        self.errlog = errlog
        self.force_compile = False # TODO make parameter

    def run(self, misuse: Misuse):
        logger = logging.getLogger("compile")
        logger.info("Compiling project version...")
        logger.debug("- Force compile     = %r", self.force_compile)
        logger.debug("- Pattern frequency = %r", self.pattern_frequency)
        logger = logging.getLogger("compile.tasks")

        checkout = misuse.get_checkout(self.checkout_base_dir)
        checkout_dir = checkout.checkout_dir
        base_path = dirname(checkout_dir)
        build_path = join(base_path, Compile.__BUILD_DIR)

        compile = ProjectCompile(checkout_dir, base_path, misuse.build_config, misuse.patterns)

        if compile.exists_copy_of_original_source() and not self.force_compile:
            logger.info("Already copied project source.")
        else:
            try:
                logger.info("Copying project sources...")
                compile.copy_original_sources()
            except IOError as e:
                logger.error("Failed to copy project sources: %s", e)
                return DataReaderSubprocess.Answer.skip

        if compile.exists_copy_of_pattern_sources() and not self.force_compile:
            logger.info("Already copied pattern sources.")
        else:
            try:
                logger.info("Copying pattern sources...")
                compile.copy_pattern_sources(self.pattern_frequency)
            except IOError as e:
                logger.error("Failed to copy pattern sources: %s", e)
                return DataReaderSubprocess.Answer.skip

        if not compile.can_compile():
            logger.warn("Skipping compilation: not configured.")
            return DataReaderSubprocess.Answer.ok

        logger.debug("Copying to build directory...")
        self._copy(checkout_dir, build_path)
        logger.debug("Copying additional resources...")
        self.copy_additional_compile_sources(misuse, build_path)

        build_config = misuse.build_config


        try:
            logger.info("Compiling project...")
            self._compile(build_config.commands, build_path)

            logger.debug("Copying project classes...")
            self._copy(join(build_path, build_config.classes), join(base_path, self.classes_normal))
        except CommandFailedError as e:
            logger.error("Compilation failed: %s", e)
            return DataReaderSubprocess.Answer.skip

        if not misuse.patterns:
            logger.info("Skipping pattern compilation: no patterns.")
            return DataReaderSubprocess.Answer.ok

        try:
            src_dir = join(build_path, build_config.src)
            logger.debug("Copying patterns to source directory...")
            patterns = set()
            for pattern in misuse.patterns:
                duplicates = pattern.duplicate(src_dir, self.pattern_frequency)
                patterns.update(duplicates)

            logger.info("Compiling patterns...")
            self._compile(build_config.commands, build_path)
            classes_dir = join(build_path, build_config.classes)

            logger.debug("Copying pattern classes...")
            for pattern in patterns:
                pattern_class_file_name = pattern.file_name + ".class"
                class_file = join(classes_dir, pattern_class_file_name)
                class_file_dest = join(base_path, self.classes_patterns, pattern_class_file_name)
                self._copy(class_file, class_file_dest)
        except CommandFailedError as e:
            logger.error("Compilation failed: %s", e)
            return DataReaderSubprocess.Answer.skip

        return DataReaderSubprocess.Answer.ok

    @staticmethod
    def copy_additional_compile_sources(misuse, checkout_dir):
        additional_sources = misuse.additional_compile_sources
        if exists(additional_sources):
            copy_tree(additional_sources, checkout_dir)

    @staticmethod
    def _compile(commands: List[str], project_dir: str) -> None:
        logger = logging.getLogger("compile.tasks.exec")
        for command in commands:
            Shell.exec(command, cwd=project_dir, logger=logger)

    # noinspection PyMethodMayBeStatic
    def _copy(self, src, dst):
        if isdir(dst):
            remove_tree(dst)

        if isdir(src):
            copy_tree(src, dst)
        elif isfile(src):
            makedirs(dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
        else:
            raise FileNotFoundError("no such file or directory {}".format(src))
