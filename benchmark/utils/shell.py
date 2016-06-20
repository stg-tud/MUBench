import os
import subprocess
import sys


class Shell:
    def __init__(self, log=sys.stdout):
        self.log = log

    def exec(self, command: str, cwd: str = os.getcwd()) -> int:
        process = subprocess.Popen(command, cwd=cwd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   shell=True)
        output, _ = process.communicate()
        output = output.decode("utf-8")
        self.log.write(output)
        return process.wait()
