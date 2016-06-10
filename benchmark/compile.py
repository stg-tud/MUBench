import os
import shutil
import subprocess
from os import makedirs
from os.path import join, exists

from typing import Set, List

from benchmark.datareader import DataReaderSubprocess
from benchmark.misuse import Misuse
from benchmark.pattern import Pattern
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

    def run(self, misuse: Misuse):
        subprocess_print("Building project... ", end='')

        project_dir = join(self.checkout_base_dir, misuse.project_name)
        checkout_dir = join(project_dir, self.checkout_subdir)
        build_config = misuse.build_config

        # copy project src
        project_src = checkout_dir if build_config is None else join(checkout_dir, build_config.src)
        self._copy(project_src, join(project_dir, self.src_normal))

        # copy patterns src
        for pattern in misuse.patterns:
            pattern.duplicate(join(project_dir, self.src_patterns), self.pattern_frequency)

        if build_config is None:
            print("no build configured for this project, continuing without compiled sources.")
            return DataReaderSubprocess.Answer.ok

        build_dir = join(project_dir, "build")

        additional_sources = misuse.additional_compile_sources
        if exists(additional_sources):
            copy_tree(additional_sources, checkout_dir)

        # create and move project classes
        self._copy(checkout_dir, build_dir)
        build_ok = self._build(build_config.commands, build_dir)
        if not build_ok:
            print("error building project!")
            return DataReaderSubprocess.Answer.skip

        self._move(join(build_dir, build_config.classes), join(project_dir, self.classes_normal))

        # create and move patterns classes
        self._copy(checkout_dir, build_dir)
        build_ok = self._build_with_patterns(build_config.commands, build_config.src, build_dir, self.pattern_frequency,
                                             misuse.patterns)
        if not build_ok:
            print("error building patterns!")
            return DataReaderSubprocess.Answer.skip

        self._move(join(build_dir, build_config.classes), join(project_dir, self.classes_patterns))

        print_ok()
        return DataReaderSubprocess.Answer.ok

    def _build(self, commands: List[str], project_dir: str) -> bool:
        for command in commands:
            ok = self._call(command, project_dir)
            if not ok:
                return False
        return True

    def _call(self, command: str, cwd: str) -> bool:
        makedirs(cwd, exist_ok=True)
        with open(self.outlog, 'a+') as outlog, open(self.errlog, 'a+') as errlog:
            returncode = subprocess.call(command, shell=True, cwd=cwd, stdout=outlog, stderr=errlog, bufsize=1)
        return returncode == 0

    def _build_with_patterns(self, commands: List[str], src: str, build_dir: str, pattern_frequency: int,
                             patterns: Set[Pattern]) -> bool:
        shutil.rmtree(join(build_dir, src), ignore_errors=True)

        for pattern in patterns:
            pattern.duplicate(join(build_dir, src), pattern_frequency)

        return self._build(commands, build_dir)

    # noinspection PyMethodMayBeStatic
    def _copy(self, src, dst):
        remove_tree(dst)
        copy_tree(src, dst)

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
