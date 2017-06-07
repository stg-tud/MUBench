from nose.tools import assert_equals
from unittest.mock import MagicMock

from tasks.implementations.requirements_check import RequirementsCheck
from tests.test_utils.data_util import create_project

from requirements import Requirement

class TestRequirementsCheck():
    def setup(self):
        self.uut = RequirementsCheck()

        self.test_requirement = Requirement("-test-requirement-")
        self.test_requirement.check = MagicMock()
        self.uut._get_requirements = lambda: [self.test_requirement]

    def test_process_project(self):
        assert_equals([], self.uut.process_project(create_project("-project-")))

    def test_checks_requirements_on_start(self):
        self.uut.start()

        self.test_requirement.check.assert_called_once_with()
