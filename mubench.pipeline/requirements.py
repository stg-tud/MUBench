import psutil
from hurry.filesize import size

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
    def __init__(self):
        super().__init__("CPUs >= 2")

    def check(self):
        cpu_count = psutil.cpu_count(logical=False)
        if cpu_count < 2:
            raise ValueError("Only {} CPUs available.".format(cpu_count))

class MemoryRequirement(Requirement):
    MIN_MEMORY = 8589934592

    def __init__(self):
        super().__init__("Memory >= {}".format(size(self.MIN_MEMORY)))

    def check(self):
        memory = psutil.virtual_memory().total
        if memory < self.MIN_MEMORY:
            raise ValueError("Only {} of memory available.".format(size(memory)))
