import logging
from os.path import exists
from typing import List

from utils.shell import Shell


class RequirementsCheck:
    def __init__(self):
        logger = logging.getLogger("tasks.requirements")
        requirements = RequirementsCheck._get_requirements()
        if RequirementsCheck._are_satisfied(requirements, logger):
            logger.info("All requirements satisfied. You're good to go.")
        else:
            logger.warning(
                "Unsatisfied requirements. Some MUBench tasks might work anyways, but to use the entire benchmark,"
                " please ensure that your environment meets all requirements.")

    def run(self):
        return [self]

    @staticmethod
    def _get_requirements() -> List['Requirement']:
        return [requirement() for requirement in Requirement.__subclasses__()]

    @staticmethod
    def _are_satisfied(requirements: List['Requirement'], logger) -> bool:
        all_satisfied = True
        for requirement in requirements:
            all_satisfied &= RequirementsCheck._is_satisfied(requirement, logger)
        return all_satisfied

    @staticmethod
    def _is_satisfied(requirement: 'Requirement', logger: logging.Logger) -> bool:
        try:
            requirement.check()
            logger.debug("Requirement '%s' satisfied", requirement.description)
            return True
        except Exception as e:
            logger.warning("Requirement '%s' not satisfied: %s", requirement.description, e)
            return False


class Requirement:
    def __init__(self, description: str, check=None):
        self.description = description
        if not check:
            check = self.check
        self.check = check

    def check(self):
        raise NotImplementedError


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

class CPUCountRequirement(Requirement):
    MIN_CPU_COUNT = 2

    def __init__(self):
        super().__init__("CPUs >= {}".format(self.MIN_CPU_COUNT))

    def check(self):
        cpu_count = self._get_cpu_count()
        if cpu_count < self.MIN_CPU_COUNT:
            raise ValueError("Only {} CPUs available.".format(cpu_count))

    def _get_cpu_count(self):
        if _in_container():
            return self._get_container_cpu_count()
        else:
            return self._get_normal_cpu_count()

    def _get_container_cpu_count(self):
        try:
            """
                cpu-quota is the guaranteed microseconds of CPU time the container will get.
                cpu-period is the scheduler period, which defaults to one second in microseconds.
                The actual access to CPUs can be calculated using 'cpu-quota / cpu-period'.
                Using '--cpus=X', docker sets the cpu-period to 100000 and cpu-quota to 100000 * X.
                The default cpu-quota is -1, hence we check the host sytem in that case.
                Example: '--cpus=1.5' means '--cpu-period=100000 --cpu-quota=150000'.
            """

            cpu_quota = self._get_cpu_quota()
            cpu_period = self._get_cpu_period()

            no_limit = cpu_quota < 0
            if no_limit:
                return self._get_normal_cpu_count()
            else:
                return cpu_quota / cpu_period

        except Exception as e:
            raise RuntimeError("Failed to check CPU count: {}".format(e))

    def _get_cpu_quota(self):
        with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us") as file:
            return int(file.readline())

    def _get_cpu_period(self):
        with open("/sys/fs/cgroup/cpu/cpu.cfs_period_us") as file:
            return int(file.readline())

    def _get_normal_cpu_count(self):
        psutil = _try_import("psutil")
        return psutil.cpu_count(logical=False)


class MemoryRequirement(Requirement):
    MIN_MEMORY = 8589934592

    def __init__(self):
        super().__init__("Memory >= {}".format(self._to_readable_size(self.MIN_MEMORY)))

    def check(self):
        memory = self._get_memory()
        if memory < self.MIN_MEMORY:
            raise ValueError("Only {} of memory available.".format(self._to_readable_size(memory)))

    def _get_memory(self):
        if _in_container():
            return self._get_container_memory_limit()
        else:
            psutil = _try_import("psutil")
            return psutil.virtual_memory().total

    def _get_container_memory_limit(self):
        try:
            with open("/sys/fs/cgroup/memory/memory.limit_in_bytes") as file:
                return int(file.readline())
        except Exception as e:
            raise RuntimeError("Failed to check memory: {}".format(e))

    def _to_readable_size(self, size_in_bytes: int) -> str:
        try:
            hf = _try_import("hurry.filesize")
            return str(hf.size(size_in_bytes))
        except ImportError:
            return str(size_in_bytes) + "B"


def _in_container() -> bool:
    return exists("/.dockerenv")

def _try_import(module):
    try:
        import importlib
        return importlib.import_module(module)
    except Exception as e:
        raise ImportError("Check requires {}: {}".format(module, e))
