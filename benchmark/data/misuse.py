import os
from glob import glob
from os.path import isdir, isfile, join, basename
from typing import Set

import yaml

from benchmark.data.build_config import BuildConfig
from benchmark.data.pattern import Pattern

# noinspection PyAttributeOutsideInit
from benchmark.data.project_checkout import LocalProjectCheckout, GitProjectCheckout, SVNProjectCheckout, \
    ProjectCheckout


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
    def project_version(self) -> str:
        project_version = None
        if '.' in self.name:
            project_version = self.name.split('.', 1)[1]
        return project_version

    @property
    def patterns(self) -> Set[Pattern]:
        if getattr(self, '_PATTERNS', None) is None:
            pattern_path = join(self.path, "patterns")
            if isdir(pattern_path):
                self._PATTERNS = set(
                    [Pattern(pattern_path, y[len(pattern_path) + 1:]) for x in os.walk(pattern_path) for y in glob(os.path.join(x[0], '*.java'))])
            else:
                self._PATTERNS = set()

        return self._PATTERNS

    @property
    def meta(self):
        if getattr(self, '_META', None) is None:
            stream = open(self.meta_file, 'r')
            try:
                self._META = yaml.load(stream)
            finally:
                stream.close()

        return self._META

    def get_checkout(self, base_path: str) -> ProjectCheckout:
        repository = self.meta["fix"]["repository"]
        if repository["type"] == "git":
            url = repository["url"]
            revision = self.meta["fix"]["revision"] + "~1"
            return GitProjectCheckout(url, base_path, self.project_name, self.project_version, revision)
        elif repository["type"] == "svn":
            url = repository["url"]
            revision = str(int(self.meta["fix"]["revision"]) - 1 )
            return SVNProjectCheckout(url, base_path, self.project_name, self.project_version, revision)
        elif repository["type"] == "synthetic":
            url = join(self.path, "compile")
            return LocalProjectCheckout(url, base_path, self.name)
        else:
            raise ValueError("unknown repository type: {}".format(repository["type"]))

    @property
    def build_config(self) -> BuildConfig:
        build = self.meta.get("build")
        if build is None:
            return None

        src = build.get("src")
        commands = build.get("commands")
        classes = build.get("classes")

        if None in [src, commands, classes]:
            return None

        return BuildConfig(src, commands, classes)

    @property
    def additional_compile_sources(self):
        return join(self.path, 'compile')

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return not self.__eq__(other)
