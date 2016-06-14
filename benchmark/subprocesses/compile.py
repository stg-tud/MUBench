import os
import shutil
import subprocess
from os import makedirs
from os.path import join, exists, isdir

from typing import Set, List

from benchmark.data.misuse import Misuse
from benchmark.data.pattern import Pattern
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import remove_tree, copy_tree
from benchmark.utils.printing import subprocess_print, print_ok


class Compile(DataReaderSubprocess):
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
        checkout_dir = join(project_dir, self.checkout_subdir)
        build_config = misuse.build_config

        self.copy_project_src(project_dir, checkout_dir, build_config)
        self.copy_pattern_src(project_dir, misuse)

        if build_config is None:
            subprocess_print("No build configured for this misuse.")
            return DataReaderSubprocess.Answer.ok

        self.copy_additional_compile_sources(misuse, checkout_dir)
        build_dir = join(project_dir, "build")

        subprocess_print("Compiling project... ", end='')

        self._copy(checkout_dir, build_dir)
        try:
            self._compile(build_config.commands, build_dir)
        except CompileError as ce:
            print("error in command '{}'!".format(ce.command_with_error))
            return DataReaderSubprocess.Answer.skip

        self._move(join(build_dir, build_config.classes), join(project_dir, self.classes_normal))

        print_ok()

        # skip pattern compilation if there's no patterns
        if len(misuse.patterns) == 0:
            print("no patterns, exiting")
            return DataReaderSubprocess.Answer.ok

        subprocess_print("Compiling patterns... ", end='')

        self._copy(checkout_dir, build_dir)
        src_dir = join(build_dir, build_config.src)
        for pattern in misuse.patterns:
            pattern.duplicate(src_dir, self.pattern_frequency)
        try:
            self._compile(build_config.commands, build_dir)
        except CompileError as ce:
            print("error in command '{}'!".format(ce.command_with_error))
            return DataReaderSubprocess.Answer.skip

        classes_dir = join(build_dir, build_config.classes)
        for pattern in misuse.patterns:
            pattern_class_file_name = pattern.file_name + ".class"
            class_file = join(classes_dir, pattern_class_file_name)
            class_file_dest = join(project_dir, self.classes_patterns, pattern_class_file_name)
            self._copy(class_file, class_file_dest)

        print_ok()
        return DataReaderSubprocess.Answer.ok

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
            shutil.copy(src, dst)

    # noinspection PyMethodMayBeStatic
    def _move(self, src, dst):
        shutil.rmtree(dst, ignore_errors=True)

        # copied from http://stackoverflow.com/a/7420617
        for src_dir, dirs, files in os.walk(src):
            dst_dir = src_dir.replace(src, dst, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.move(src_file, dst_dir)


class CompileError(Exception):
    def __init__(self, command_with_error: str):
        self.command_with_error = command_with_error
