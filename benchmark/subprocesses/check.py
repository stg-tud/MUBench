import inspect
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


class Check(DataReaderSubprocess):
    def setup(self):
        print("Checking prerequisites... ", end='', flush=True)

        missing_prerequisites = []
        for prerequisite_name, prerequisite_check in inspect.getmembers(Prerequisites, predicate=inspect.isfunction):
            # noinspection PyBroadException
            try:
                prerequisite_check()
            except:
                missing_prerequisites.append(prerequisite_name)

        if missing_prerequisites:
            error_message = "ERROR! Missing Prerequisites: "
            error_message += ", ".join(missing_prerequisites)
            sys.exit(error_message)

        else:
            print("Prerequisites okay!")

    def run(self, misuse: Misuse) -> DataReaderSubprocess.Answer:
        return DataReaderSubprocess.Answer.ok
