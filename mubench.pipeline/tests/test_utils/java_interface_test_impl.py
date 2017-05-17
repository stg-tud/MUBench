from unittest.mock import MagicMock

from data.java_interface import JavaInterface

class JavaInterfaceTestImpl(JavaInterface):
    TEST_VERSION = "V_TEST"

    def __init__(self, jar_path, java_options):
        super().__init__(jar_path, java_options)
        self.execute = MagicMock()

    @staticmethod
    def version() -> str:
        return JavaInterfaceTestImpl.TEST_VERSION
