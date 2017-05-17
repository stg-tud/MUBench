from unittest.mock import MagicMock

from data.runner_interface import RunnerInterface

class RunnerInterfaceTestImpl(RunnerInterface):
    TEST_VERSION = "V_TEST"

    def __init__(self, jar_path, java_options):
        super().__init__(jar_path, java_options)
        self.execute = MagicMock()

    @staticmethod
    def version() -> str:
        return RunnerInterfaceTestImpl.TEST_VERSION
