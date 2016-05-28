import subprocess
from distutils.dir_util import copy_tree
from os import makedirs
from os.path import join, exists

from benchmark.datareader import Continue
from benchmark.misuse import Misuse
from benchmark.utils.printing import subprocess_print, print_ok


class Compile:
    def __init__(self, checkout_base_dir: str, outlog: str, errlog: str):
        self.checkout_base_dir = checkout_base_dir
        self.outlog = outlog
        self.errlog = errlog

    def build(self, misuse: Misuse):
        subprocess_print("Building project... ", end='')

        project_dir = join(self.checkout_base_dir, misuse.project_name)

        additional_sources = misuse.additional_compile_sources
        if exists(additional_sources):
            copy_tree(additional_sources, project_dir, verbose=0)

        build_config = misuse.build_config

        if build_config is None or build_config.commands is None:
            print("no commands specified, continuing without compiled sources.")
            return

        for command in build_config.commands:
            ok = self._call(command, project_dir)
            if not ok:
                print("error in command {}!".format(command))
                raise Continue

        print_ok()

    def _call(self, command: str, cwd: str) -> bool:
        makedirs(cwd, exist_ok=True)
        with open(self.outlog, 'a+') as outlog, open(self.errlog, 'a+') as errlog:
            returncode = subprocess.call(command, shell=True, cwd=cwd, stdout=outlog, stderr=errlog, bufsize=1)
        return returncode == 0
