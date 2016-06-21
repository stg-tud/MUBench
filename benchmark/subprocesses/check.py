import inspect
import logging
import subprocess
import sys

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.datareader import DataReaderSubprocess


# noinspection PyPep8Naming
class Prerequisites:
    @staticmethod
    def Git():
        subprocess.check_output(['git', '--version'], stderr=subprocess.PIPE)

    @staticmethod
    def SVN():
        subprocess.check_output(['svn', '--version', '--quiet'], stderr=subprocess.PIPE)

    @staticmethod
    def Java():
        subprocess.check_output(['java', '-version'], stderr=subprocess.PIPE)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def PyYAML():
        import yaml

    # noinspection PyUnresolvedReferences
    @staticmethod
    def request():
        import urllib.request

    @staticmethod
    def gradle():
        subprocess.check_output(['gradle', '-version'], stderr=subprocess.PIPE)

    @staticmethod
    def maven():
        subprocess.check_output(['mvn', '-v'])


class Check(DataReaderSubprocess):
    def __init__(self):
        self._logger = logging.getLogger()

    def setup(self):
        missing_prerequisites = False
        for prerequisite_name, prerequisite_check in inspect.getmembers(Prerequisites, predicate=inspect.isfunction):
            # noinspection PyBroadException
            try:
                prerequisite_check()
                self._logger.debug("Prerequisite '%s' satisfied", prerequisite_name)
            except:
                self._logger.error("Prerequisite '%s' not satisfied", prerequisite_name)
                missing_prerequisites = True

        if missing_prerequisites:
            self._logger.error("Cannot run MUBench. Please provide prerequisites.")
            sys.exit("Cannot run MUBench. Please provide prerequisites.")
        else:
            self._logger.info("Prerequisites ok.")

    def run(self, misuse: Misuse) -> DataReaderSubprocess.Answer:
        return DataReaderSubprocess.Answer.ok
