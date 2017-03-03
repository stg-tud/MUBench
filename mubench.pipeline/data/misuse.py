import os
from glob import glob
from os.path import isdir, isfile, join
from typing import Set, List

import yaml

from data.pattern import Pattern
from data.snippets import get_snippets, Snippet


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

        from data.project import Project
        self.__project = Project(base_path, project_id)

        self.path = join(self.__project.path, Project.MISUSES_DIR, misuse_id)
        self.misuse_file = join(self.path, Misuse.MISUSE_FILE)

        self.__location = None
        self.__fix = None

        self._YAML = None
        self._PATTERNS = []

    @property
    def _yaml(self):
        if not self._YAML:
            with open(self.misuse_file, 'r') as stream:
                self._YAML = yaml.load(stream)
        return self._YAML

    @property
    def patterns(self) -> Set[Pattern]:
        if not self._PATTERNS:
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
            self.__location = Location(location.get("file", ""), location.get("method", ""))
        return self.__location

    @property
    def description(self) -> str:
        if getattr(self, '_DESCRIPTION', None) is None:
            description = self._yaml.get("description", "")
            self._DESCRIPTION = description
        return self._DESCRIPTION

    @property
    def fix(self) -> Fix:
        if not self.__fix:
            fix = self._yaml.get("fix", {})
            self.__fix = Fix(fix.get("description", ""), fix.get("commit", ""), str(fix.get("revision", "")))
        return self.__fix

    @property
    def is_crash(self) -> bool:
        if getattr(self, '_IS_CRASH', None) is None:
            self._IS_CRASH = self._yaml["crash"]
        return self._IS_CRASH

    @property
    def source(self):
        if getattr(self, '_source', None) is None:
            source_key = self._yaml.get('source', None)
            if source_key is not None:
                self._source = source_key.get('name', None)
        return self._source

    @property
    def challenges(self):
        if getattr(self, '_challenges', None) is None:
            self._challenges = self._yaml.get('challenges', [])
        return self._challenges

    @property
    def characteristics(self):
        if getattr(self, '_characteristics', None) is None:
            self._characteristics = self._yaml.get('characteristics', [])
        return self._characteristics

    def get_snippets(self, source_base_path: str) -> List[Snippet]:
        return get_snippets(source_base_path, self.location.file, self.location.method)

    def __str__(self):
        return "misuse '{}'".format(self.id)

    def __hash__(self):
        return self.path.__hash__()

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return not self.__eq__(other)
