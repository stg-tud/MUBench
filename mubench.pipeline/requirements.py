import psutil
from hurry.filesize import size
from os.path import exists
from utils.shell import Shell


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
            return psutil.cpu_count(logical=False)

    def _get_container_cpu_count(self):
        try:
            with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us") as file:
                return int(file.readline()) / 100000
        except Exception as e:
            raise RuntimeError("Failed to check CPU count: {}".format(e))


class MemoryRequirement(Requirement):
    MIN_MEMORY = 8589934592

    def __init__(self):
        super().__init__("Memory >= {}".format(size(self.MIN_MEMORY)))

    def check(self):
        memory = self._get_memory()
        if memory < self.MIN_MEMORY:
            raise ValueError("Only {} of memory available.".format(size(memory)))

    def _get_memory(self):
        if _in_container():
            return self._get_container_memory_limit()
        else:
            return psutil.virtual_memory().total

    def _get_container_memory_limit(self):
        try:
            with open("/sys/fs/cgroup/memory/memory.limit_in_bytes") as file:
                return int(file.readline())
        except Exception as e:
            raise RuntimeError("Failed to check memory: {}".format(e))


def _in_container() -> bool:
    return exists("/.dockerenv")
