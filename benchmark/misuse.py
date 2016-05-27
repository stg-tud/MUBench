import yaml
from os import listdir
from os.path import isdir, isfile, join, basename
from typing import Set, List


# noinspection PyAttributeOutsideInit
class Misuse:
    META_FILE = "meta.yml"

    @staticmethod
    def ismisuse(path: str) -> bool:
        return isdir(path) and isfile(join(path, Misuse.META_FILE))

    def __init__(self, path: str):
        self.path = path
        self.name = basename(path)
        self.meta_file = join(path, Misuse.META_FILE)

    @property
    def project_name(self) -> str:
        project_name = self.name
        if '.' in project_name:
            project_name = project_name.split('.', 1)[0]
        return project_name

    @property
    def pattern(self) -> Set[str]:
        pattern_path = join(self.path, "pattern")
        if isdir(pattern_path):
            return set([join(pattern_path, file) for file in listdir(pattern_path)])
        else:
            return set()

    @property
    def meta(self):
        if getattr(self, '_META', None) is None:
            stream = open(self.meta_file, 'r')
            try:
                self._META = yaml.load(stream)
            finally:
                stream.close()

        return self._META

    @property
    def repository(self):
        repository = self.meta["fix"]["repository"]
        if repository["type"] == "synthetic":
            repository["url"] = join(self.path, "compile")
        return Repository(repository["type"], repository["url"])

    @property
    def fix_revision(self):
        return self.meta["fix"].get("revision", None)

    @property
    def build_config(self):
        build = self.meta.get("build")
        if build is None:
            return None

        return BuildConfig(build["src"], build["commands"], build["classes"])

    @property
    def additional_compile_sources(self):
        return join(self.path, 'compile')

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return not self.__eq__(other)


class Repository:
    def __init__(self, type: str, url: str):
        self.type = type
        self.url = url


class BuildConfig:
    def __init__(self, src: str, commands: List[str], classes: str):
        self.src = src
        self.commands = commands
        self.classes = classes
