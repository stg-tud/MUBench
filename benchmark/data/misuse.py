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



# noinspection PyAttributeOutsideInit
class Misuse:
    MISUSE_FILE = "misuse.yml"

    @staticmethod
    def ismisuse(path: str) -> bool:
        return isdir(path) and isfile(join(path, Misuse.MISUSE_FILE))

    def __init__(self, path: str):
        self.path = path
        self._path = path
        self.name = basename(path)
        self.misuse_file = join(path, Misuse.MISUSE_FILE)

    @property
    def _yaml(self):
        if getattr(self, '_YAML', None) is None:
            with open(self.misuse_file, 'r') as stream:
                self._YAML = yaml.load(stream)
        return self._YAML

    @property
    def id(self):
        return basename(self._path)

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
    def usage(self) -> str:
        if getattr(self, '_USAGE', None) is None:
            self._USAGE = self._yaml.get('usage', '')
        return self._USAGE

    @property
    def location(self) -> Location:
        location = self._yaml["location"]
        return Location(location["file"], location["method"])

    def __str__(self):
        return "misuse '{}'".format(self.name)

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return not self.__eq__(other)
