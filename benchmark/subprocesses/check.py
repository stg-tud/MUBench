import inspect
import logging
import subprocess
import sys


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


def check_prerequisites():
    logger = logging.getLogger()
    missing_prerequisites = False
    for prerequisite_name, prerequisite_check in inspect.getmembers(Prerequisites, predicate=inspect.isfunction):
        # noinspection PyBroadException
        try:
            prerequisite_check()
            logger.debug("Prerequisite '%s' satisfied", prerequisite_name)
        except:
            logger.error("Prerequisite '%s' not satisfied", prerequisite_name)
            missing_prerequisites = True

    if missing_prerequisites:
        logger.error("Cannot run MUBench. Please provide prerequisites.")
        sys.exit("Cannot run MUBench. Please provide prerequisites.")
    else:
        logger.info("Prerequisites ok.")
