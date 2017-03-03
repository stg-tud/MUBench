import logging
from typing import List

from tasks.project_task import Requirement
from utils.shell import Shell


def check_all_requirements():
    logger = logging.getLogger("requirements")
    logger.info("Checking all requirements...")
    requirements = map(lambda requirement: requirement(), Requirement.__subclasses__())  # type: List[Requirement]
    if are_satisfied(requirements, logger):
        logger.info("All requirements satisfied. You're good to go.")
    else:
        logger.info("Unsatisfied requirements. Some MUBench tasks might work anyways, but to use the entire benchmark,"
                    " please ensure that your environment meets all requirements.")


def are_satisfied(requirements: List[Requirement], logger) -> bool:
    all_satisfied = True
    for requirement in requirements:
        all_satisfied &= is_satisfied(requirement, logger)
    return all_satisfied


def is_satisfied(requirement: Requirement, logger: logging.Logger) -> bool:
    try:
        requirement.check()
        logger.debug("Requirement '%s' satisfied", requirement.description)
        return True
    except Exception as e:
        logger.error("Requirement '%s' not satisfied: %s", requirement.description, e)
        return False


class PyYamlRequirement(Requirement):
    def __init__(self):
        super().__init__("PyYaml")

    def check(self):
        pass


class GitRequirement(Requirement):
    def __init__(self):
        super().__init__("git 2.0+")

    def check(self):
        Shell.exec("git --version")


class SVNRequirement(Requirement):
    def __init__(self):
        super().__init__("svn 1.8+")

    def check(self):
        Shell.exec("svn --version")


class JavaRequirement(Requirement):
    def __init__(self):
        super().__init__("Java 8+")

    def check(self):
        Shell.exec("java -version")


class MavenRequirement(Requirement):
    def __init__(self):
        super().__init__("Maven 3.3.0+")

    def check(self):
        Shell.exec("mvn -v")


class GradleRequirement(Requirement):
    def __init__(self):
        super().__init__("Gradle 1.10+")

    def check(self):
        Shell.exec("gradle -version")


class DotRequirement(Requirement):
    def __init__(self):
        super().__init__("Dot 2.38+")

    def check(self):
        Shell.exec("dot -V")


class RequestsRequirement(Requirement):
    def __init__(self):
        super().__init__("requests 2.11.1")

    def check(self):
        pass