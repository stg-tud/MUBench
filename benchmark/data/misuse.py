import os
import yaml
from glob import glob
from os.path import isdir, isfile, join, basename
from typing import Set, List

from benchmark.data.pattern import Pattern


class Location:
    def __init__(self, file: str, method: str):
        self.file = file
        self.method = method

    def __str__(self):
        return "Location({}, {})".format(self.file, self.method)

    def __eq__(self, other):
        return self.file == other.file and self.method == other.method


class Fix:
    def __init__(self, description: str, commit: str, revision: str):
        self.description = description
        self.commit = commit
        self.revision = revision


class Misuse:
    MISUSE_FILE = "misuse.yml"

    @staticmethod
    def is_misuse(path: str) -> bool:
        return isfile(join(path, Misuse.MISUSE_FILE))

    def __init__(self, base_path: str, project_id: str, misuse_id: str):
        self._base_path = base_path
        self.project_id = project_id
        self.misuse_id = misuse_id
        self.id = "{}.{}".format(project_id, misuse_id)

        from benchmark.data.project import Project
        self.__project = Project(base_path, project_id)

        self.path = join(self.__project.path, Project.MISUSES_DIR, misuse_id)
        self.misuse_file = join(self.path, Misuse.MISUSE_FILE)

        self.__location = None
        self.__fix = None

    @property
    def _yaml(self):
        if getattr(self, '_YAML', None) is None:
            with open(self.misuse_file, 'r') as stream:
                self._YAML = yaml.load(stream)
        return self._YAML

    @property
    def patterns(self) -> Set[Pattern]:
        if getattr(self, '_PATTERNS', None) is None:
            pattern_path = join(self.path, "patterns")
            if isdir(pattern_path):
                self._PATTERNS = set(
                    [Pattern(pattern_path, y[len(pattern_path) + 1:]) for x in os.walk(pattern_path) for y in
                     glob(os.path.join(x[0], '*.java'))])
            else:
                self._PATTERNS = set()

        return self._PATTERNS

    @property
    def location(self) -> Location:
        if not self.__location:
            location = self._yaml["location"]
            self.__location = Location(location["file"], location["method"])
        return self.__location

    @property
    def description(self) -> str:
        return self._yaml.get("description", "")

    @property
    def fix(self) -> Fix:
        if not self.__fix:
            fix = self._yaml.get("fix", {})
            self.__fix = Fix(fix.get("description", ""), fix.get("commit", ""), str(fix.get("revision", "")))
        return self.__fix

    def __str__(self):
        return "misuse '{}'".format(self.id)

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return not self.__eq__(other)
