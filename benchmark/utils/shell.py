import logging
import os
from subprocess import check_output, STDOUT, CalledProcessError
from typing import Optional


class Shell:
    @staticmethod
    def exec(command: str, cwd: str = os.getcwd(), logger=logging.getLogger(__name__), timeout: Optional[int] = None):
        logger.debug("Execute '%s' in '%s'", command, cwd)
        try:
            output = check_output(command, cwd=cwd, bufsize=1, stderr=STDOUT, shell=True, timeout=timeout)
            output = output.decode("utf-8")
            logger.debug(output[:-1])
            return output
        except CalledProcessError as e:
            raise CommandFailedError(e.cmd, e.output.decode("utf-8"))

    @staticmethod
    def try_exec(command: str, cwd: str = os.getcwd(), logger=logging.getLogger(__name__),
                 timeout: Optional[int] = None) -> bool:
        try:
            Shell.exec(command, cwd=cwd, logger=logger, timeout=timeout)
            return True
        except CommandFailedError:
            return False


class CommandFailedError(Exception):
    def __init__(self, command: str, output: str):
        self.command = command
        self.output = output

    def __str__(self):
        return "Failed to execute '{}': {}".format(self.command, self.output)
