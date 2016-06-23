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

        checkout = misuse.get_checkout(self.checkout_base_dir)
        checkout_dir = checkout.checkout_dir
        base_path = dirname(checkout_dir)
        build_dir = join(base_path, Compile.__BUILD_DIR)

        compile = ProjectCompile(checkout_dir, base_path, misuse.build_config, misuse.patterns)

        # TODO fixme
        #self.clean(base_path, build_dir)

        if not compile.exists_copy_of_original_source() or self.force_compile:
            try:
                compile.copy_original_sources()
            except IOError as e:
                logger.error("Failed to copy project sources: %s", e)
                return DataReaderSubprocess.Answer.skip

        if not compile.exists_copy_of_pattern_sources() or self.force_compile:
            try:
                compile.copy_pattern_sources(self.pattern_frequency)
            except IOError as e:
                logger.error("Failed to copy pattern sources: %s", e)
                return DataReaderSubprocess.Answer.skip

        if not compile.can_compile():
            logger.warn("Skipping compilation: not configured.")
            return DataReaderSubprocess.Answer.ok

        project_dir = base_path

        build_config = misuse.build_config

        self.copy_additional_compile_sources(misuse, checkout_dir)

        try:
            subprocess_print("Compiling project... ", end='')
            self._copy(checkout_dir, build_dir)
            self._compile(build_config.commands, build_dir)
            self._copy(join(build_dir, build_config.classes), join(project_dir, self.classes_normal))
            print_ok()
        except CompileError as ce:
            print("error in command '{}'!".format(ce.command_with_error))
            return DataReaderSubprocess.Answer.skip

        if not misuse.patterns:
            return DataReaderSubprocess.Answer.ok

        try:
            subprocess_print("Compiling patterns... ", end='')

            self._copy(checkout_dir, build_dir)
            src_dir = join(build_dir, build_config.src)
            patterns = set()
            for pattern in misuse.patterns:
                duplicates = pattern.duplicate(src_dir, self.pattern_frequency)
                patterns.update(duplicates)
            self._compile(build_config.commands, build_dir)
            classes_dir = join(build_dir, build_config.classes)
            for pattern in patterns:
                pattern_class_file_name = pattern.file_name + ".class"
                class_file = join(classes_dir, pattern_class_file_name)
                class_file_dest = join(project_dir, self.classes_patterns, pattern_class_file_name)
                self._copy(class_file, class_file_dest)
            print_ok()
        except CompileError as ce:
            print("error in command '{}'!".format(ce.command_with_error))
            return DataReaderSubprocess.Answer.skip

        return DataReaderSubprocess.Answer.ok

    def clean(self, project_dir, build_dir):
        remove_tree(join(project_dir, self.src_normal))
        remove_tree(join(project_dir, self.classes_normal))
        remove_tree(join(project_dir, self.src_patterns))
        remove_tree(join(project_dir, self.classes_patterns))
        remove_tree(build_dir)

    @staticmethod
    def copy_additional_compile_sources(misuse, checkout_dir):
        additional_sources = misuse.additional_compile_sources
        if exists(additional_sources):
            copy_tree(additional_sources, checkout_dir)

    def _compile(self, commands: List[str], project_dir: str) -> None:
        for command in commands:
            ok = self._call(command, project_dir)
            if not ok:
                raise CompileError(command)

    def _call(self, command: str, cwd: str) -> bool:
        makedirs(cwd, exist_ok=True)
        with open(join(self.checkout_base_dir, self.outlog), 'a+') as outlog, \
                open(join(self.checkout_base_dir, self.errlog), 'a+') as errlog:
            returncode = subprocess.call(command, shell=True, cwd=cwd, stdout=outlog, stderr=errlog, bufsize=1)
        return returncode == 0

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

    # noinspection PyMethodMayBeStatic
    def _move(self, src, dst):
        remove_tree(dst)

        # copied from http://stackoverflow.com/a/7420617
        for src_dir, dirs, files in os.walk(src):
            dst_dir = join(dst, src_dir[len(src):])
            makedirs(dst_dir, exist_ok=True)
            for file_ in files:
                src_file = join(src_dir, file_)
                dst_file = join(dst_dir, file_)
                if exists(dst_file):
                    os.remove(dst_file)
                shutil.move(src_file, dst_dir)


class CompileError(Exception):
    def __init__(self, command_with_error: str):
        self.command_with_error = command_with_error
