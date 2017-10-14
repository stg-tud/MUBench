from unittest.mock import MagicMock

from nose.tools import assert_equals

from requirements import Requirement
from tasks.implementations.requirements_check import RequirementsCheck


class TestRequirementsCheck:
    def test_passes_on_process_project(self):
        self.uut = RequirementsCheck()
        assert_equals([self.uut], self.uut.run())

    def test_checks_requirements_on_start(self):
        self.test_requirement = Requirement("-test-requirement-")
        self.test_requirement.check = MagicMock()
        orig_get_requirements = RequirementsCheck._get_requirements
        RequirementsCheck._get_requirements = lambda: [self.test_requirement]
        try:
            self.uut = RequirementsCheck()
            self.test_requirement.check.assert_called_once_with()
        finally:
            RequirementsCheck._get_requirements = orig_get_requirements
