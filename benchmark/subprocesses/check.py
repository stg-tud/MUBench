import inspect
import logging
import sys

from benchmark.utils.shell import Shell


# noinspection PyPep8Naming
class Prerequisites:
    @staticmethod
    def Git():
        Shell.exec('git --version')

    @staticmethod
    def SVN():
        Shell.exec('svn --version')

    @staticmethod
    def Java():
        Shell.exec('java -version')

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
        Shell.exec('gradle -version')

    @staticmethod
    def maven():
        Shell.exec('mvn -v')


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
