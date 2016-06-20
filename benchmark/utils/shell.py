import os
import subprocess
import sys


class Shell:
    def __init__(self, log=sys.stdout):
        self.log = log

    def exec(self, command: str, cwd: str = os.getcwd()):
        process = subprocess.Popen(command, cwd=cwd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   shell=True)
        output, _ = process.communicate()
        output = output.decode("utf-8")
        self.log.write(output)
        if process.wait():
            raise CommandFailedError(command, output)

    def try_exec(self, command: str, cwd: str = os.getcwd()) -> bool:
        try:
            self.exec(command, cwd=cwd)
            return True
        except CommandFailedError:
            return False


class CommandFailedError(Exception):
    def __init__(self, command: str, output: str):
        self.command = command
        self.output = output

