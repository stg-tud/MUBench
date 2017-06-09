from distutils.version import StrictVersion
from unittest.mock import MagicMock

from data.runner_interface import RunnerInterface

class RunnerInterfaceTestImpl(RunnerInterface):
    TEST_VERSION = "0.0.0"

    def __init__(self, jar_path, java_options):
        super().__init__(jar_path, java_options)
        self.execute = MagicMock()

    @staticmethod
    def version() -> StrictVersion:
        return StrictVersion(RunnerInterfaceTestImpl.TEST_VERSION)
