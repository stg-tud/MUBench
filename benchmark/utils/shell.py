import logging
import os
import subprocess


class Shell:
    @staticmethod
    def exec(command: str, cwd: str = os.getcwd(), logger=logging.getLogger(__name__)):
        process = subprocess.Popen(command, cwd=cwd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   shell=True)
        output, _ = process.communicate()
        output = output.decode("utf-8")
        logger.debug(output)
        if process.wait():
            raise CommandFailedError(command, output)
        else:
            return output

    @staticmethod
    def try_exec(command: str, cwd: str = os.getcwd(), logger=logging.getLogger(__name__)) -> bool:
        try:
            Shell.exec(command, cwd=cwd, logger=logger)
            return True
        except CommandFailedError:
            return False


class CommandFailedError(Exception):
    def __init__(self, command: str, output: str):
        self.command = command
        self.output = output

    def __str__(self):
        return "failed to execute {}: {}".format(self.command, self.output)
