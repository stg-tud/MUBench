import inspect
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
    def PyYAMLPackage():
        import yaml

    # noinspection PyUnresolvedReferences
    @staticmethod
    def RequestPackage():
        import request


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
