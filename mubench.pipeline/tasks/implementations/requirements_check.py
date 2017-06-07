import logging
from typing import List

from requirements import Requirement
from tasks.project_task import ProjectTask
from utils.shell import Shell


class RequirementsCheck(ProjectTask):
    def __init__(self):
        super().__init__()

    def start(self):
        logger = logging.getLogger("requirements")
        requirements = self._get_requirements()
        if RequirementsCheck._are_satisfied(requirements, logger):
            logger.info("All requirements satisfied. You're good to go.")
        else:
            logger.warning("Unsatisfied requirements. Some MUBench tasks might work anyways, but to use the entire benchmark,"
                        " please ensure that your environment meets all requirements.")

    def process_project(self, *_):
        return self.ok()

    def _get_requirements(self) -> List[Requirement]:
        return [requirement() for requirement in Requirement.__subclasses__()]

    @staticmethod
    def _are_satisfied(requirements: List[Requirement], logger) -> bool:
        all_satisfied = True
        for requirement in requirements:
            all_satisfied &= RequirementsCheck._is_satisfied(requirement, logger)
        return all_satisfied

    @staticmethod
    def _is_satisfied(requirement: Requirement, logger: logging.Logger) -> bool:
        try:
            requirement.check()
            logger.debug("Requirement '%s' satisfied", requirement.description)
            return True
        except Exception as e:
            logger.warning("Requirement '%s' not satisfied: %s", requirement.description, e)
            return False

