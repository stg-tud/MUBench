import os
import shutil
import subprocess
from os import makedirs
from os.path import join, exists, isdir, dirname

from typing import List

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import remove_tree, copy_tree
from benchmark.utils.printing import subprocess_print, print_ok


class Compile(DataReaderSubprocess):
    BUILD_DIR = "build"

    def __init__(self, checkout_base_dir: str, checkout_subdir: str, src_normal: str, classes_normal: str,
                 src_patterns: str, classes_patterns: str, pattern_frequency: int, outlog: str, errlog: str):
        self.checkout_base_dir = checkout_base_dir
        self.checkout_subdir = checkout_subdir
        self.src_normal = src_normal
        self.classes_normal = classes_normal
        self.src_patterns = src_patterns
        self.classes_patterns = classes_patterns
        self.pattern_frequency = pattern_frequency
        self.outlog = outlog
        self.errlog = errlog

        self.command_with_error = ""

    def run(self, misuse: Misuse):
        project_dir = join(self.checkout_base_dir, misuse.project_name)
        build_dir = join(project_dir, Compile.BUILD_DIR)

        self.clean(project_dir, build_dir)

        checkout_dir = join(project_dir, self.checkout_subdir)
        build_config = misuse.build_config

        self.copy_project_src(project_dir, checkout_dir, build_config)
        self.copy_pattern_src(project_dir, misuse)

        if build_config is None:
            subprocess_print("No compilation configured for this misuse.")
            return DataReaderSubprocess.Answer.ok

        self.copy_additional_compile_sources(misuse, checkout_dir)

        try:
            subprocess_print("Compiling project... ", end='')
            self._copy(checkout_dir, build_dir)
            self._compile(build_config.commands, build_dir)
            self._move(join(build_dir, build_config.classes), join(project_dir, self.classes_normal))
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

    def copy_pattern_src(self, project_dir, misuse):
        for pattern in misuse.patterns:
            pattern.duplicate(join(project_dir, self.src_patterns), self.pattern_frequency)

    def copy_project_src(self, project_dir, checkout_dir, build_config):
        project_src = checkout_dir if build_config is None else join(checkout_dir, build_config.src)
        self._copy(project_src, join(project_dir, self.src_normal))

    def _compile(self, commands: List[str], project_dir: str) -> None:
        for command in commands:
            ok = self._call(command, project_dir)
            if not ok:
                raise CompileError(command)

    def _call(self, command: str, cwd: str) -> bool:
        makedirs(cwd, exist_ok=True)
        with open(self.outlog, 'a+') as outlog, open(self.errlog, 'a+') as errlog:
            returncode = subprocess.call(command, shell=True, cwd=cwd, stdout=outlog, stderr=errlog, bufsize=1)
        return returncode == 0

    # noinspection PyMethodMayBeStatic
    def _copy(self, src, dst):
        if isdir(dst):
            remove_tree(dst)

        if isdir(src):
            copy_tree(src, dst)
        else:
            makedirs(dirname(dst), exist_ok=True)
            shutil.copy(src, dst)

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
