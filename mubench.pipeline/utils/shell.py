import locale
import logging
import os
from platform import platform
from subprocess import PIPE, STDOUT, CalledProcessError, run, TimeoutExpired
from typing import Optional


class Shell:
    @staticmethod
    def exec(command: str, cwd: str = os.getcwd(), logger=logging.getLogger(__name__), timeout: Optional[int] = None):
        logger.debug("Execute '%s' in '%s'", command, cwd)
        encoding = Shell.__get_encoding()
        try:
            # On our Debian server subprocess does not return until after the process finished, but then correctly
            # raises TimeoutExpired, if the process took to long. We use `timeout` to ensure that the process terminates
            # eventually.
            if "debian" in platform() and timeout is not None:
                command = "timeout {} {}".format(timeout + 60, command)

            output = Shell.__exec(command, cwd, timeout, encoding)
            logger.debug(output)
            return output
        except CalledProcessError as e:
            raise CommandFailedError(e.cmd, e.output.decode(encoding), e.stderr.decode(encoding))
        except TimeoutExpired as e:
            raise TimeoutError(e.cmd, e.output.decode(encoding))

    @staticmethod
    def __get_encoding():
        return locale.getpreferredencoding()

    @staticmethod
    def __exec(command, cwd, timeout, encoding):
        cmd = run(command, cwd=cwd, stdout=PIPE, stderr=PIPE, shell=True, check=True, timeout=timeout)
        try:
            stdout = cmd.stdout.decode(encoding)
            stderr = cmd.stderr.decode(encoding)
        except MemoryError:
            return "Too much output to process..."
        else:
            return _combined_output(stdout, stderr)

    @staticmethod
    def try_exec(command: str, cwd: str = os.getcwd(), logger=logging.getLogger(__name__),
                 timeout: Optional[int] = None) -> bool:
        try:
            Shell.exec(command, cwd=cwd, logger=logger, timeout=timeout)
            return True
        except CommandFailedError as e:
            logger.debug(e)
            return False


class CommandFailedError(Exception):
    def __init__(self, command: str, output: str, error: str = ""):
        self.command = command
        self.output = output
        self.error = error

    def __str__(self):
        message = "Failed to execute '{}': {}".format(
                        self.command, _combined_output(self.output, self.error))
        return message


def _combined_output(stdout: str, stderr: str) -> str:
    combined_output = ""
    if stdout:
        if stderr:
            combined_output += "=== OUT ===" + os.linesep
        combined_output += stdout
    if stderr:
        combined_output += "=== ERROR ===" + os.linesep
        combined_output += stderr
    return combined_output
