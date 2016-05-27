import subprocess
from os.path import join, exists

from shutil import copytree

from benchmark.misuse import Misuse


class Compile:
    def __init__(self, checkout_base_dir: str, outlog: str, errlog: str):
        self.checkout_base_dir = checkout_base_dir
        self.outlog = outlog
        self.errlog = errlog

    def build(self, misuse: Misuse):
        additional_sources = misuse.additional_compile_sources
        if exists(additional_sources):
            copytree(additional_sources, join(self.checkout_base_dir, misuse.project_name))

        build_config = misuse.build_config

        if build_config is None:
            return

        for command in build_config.commands:
            self._call(command)

    def _call(self, command: str):
        with open(self.outlog, 'a+') as outlog, open(self.errlog, 'a+') as errlog:
            subprocess.call(command, shell=True, stdout=outlog, stderr=errlog, bufsize=1)
