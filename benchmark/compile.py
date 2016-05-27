import subprocess

from benchmark.misuse import Misuse


class Compile:
    def __init__(self, outlog: str, errlog: str):
        self.outlog = outlog
        self.errlog = errlog

    def build(self, misuse: Misuse):
        build_config = misuse.build_config

        if build_config is None:
            return

        for command in build_config.commands:
            self._call(command)

    def _call(self, command: str):
        with open(self.outlog, 'a+') as outlog, open(self.errlog, 'a+') as errlog:
            subprocess.call(command, shell=True, stdout=outlog, stderr=errlog, bufsize=1)
