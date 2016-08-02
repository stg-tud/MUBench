import inspect
import logging
import sys

from benchmark.subprocesses.tasks.base.project_task import Requirement
from benchmark.utils.shell import Shell


class PyYamlRequirement(Requirement):
    def __init__(self):
        super().__init__("PyYaml")

    def check(self):
        import yaml


class UrlLibRequirement(Requirement):
    def __init__(self):
        super().__init__("urllib")

    def check(self):
        import urllib.request


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
