from nose.tools import assert_equals
from unittest.mock import MagicMock

from tasks.implementations.check import Check
from tests.test_utils.data_util import create_project


class TestCheck():
    def test_process_project(self):
        assert_equals([], Check().process_project(create_project("-project-")))

    def test_checks_requirements_on_start(self):
        uut = Check()
        uut._check_all_requirements = MagicMock()

        uut.start()

        uut._check_all_requirements.assert_called_once_with()
