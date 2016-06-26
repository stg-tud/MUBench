import yaml
from os import listdir
from os.path import exists, pardir, isdir, realpath, basename
from os.path import join
from typing import List, Optional, Any, Dict, Set

from benchmark.data.build_config import BuildConfig
from benchmark.data.misuse import Misuse, Pattern


# noinspection PyAttributeOutsideInit
class ProjectVersion:
    VERSION_FILE = 'version.yml'

    def __init__(self, path: str):
        self._path = path  # type: str
        self._version_file = join(self._path, ProjectVersion.VERSION_FILE)  # type: str
        self._misuses_dir = realpath(join(self._path, pardir, pardir, 'misuses'))  # type: str
        self._YAML = None
        self._MISUSES = None
        self._PATTERNS = None

    @staticmethod
    def validate(path: str) -> bool:
        return exists(join(path, ProjectVersion.VERSION_FILE))

    @property
    def id(self):
        return basename(self._path)

    @property
    def _yaml(self) -> Dict[str, Any]:
        if self._YAML is None:
            with open(self._version_file) as stream:
                version_yml = yaml.load(stream)
            self._YAML = version_yml
        return self._YAML

    @property
    def __compile(self):
        compile = {"src": "", "commands": [], "classes": ""}
        compile.update(self._yaml.get("build", {}))
        return compile

    @property
    def source_dir(self):
        return self.__compile["src"]

    @property
    def compile_commands(self):
        return self.__compile["commands"]

    @property
    def classes_dir(self):
        return self.__compile["classes"]

    @property
    def misuses(self) -> List[Misuse]:
        if not self._MISUSES:
            my_misuse_ids = self._yaml.get("misuses", None)
            if my_misuse_ids is None:
                return []

            misuses_dir = self._misuses_dir
            if not exists(misuses_dir):
                return []

            my_misuses = []
            misuses = [join(misuses_dir, misuse) for misuse in listdir(misuses_dir) if isdir(join(misuses_dir, misuse))]
            for misuse in misuses:
                if Misuse.ismisuse(misuse) and Misuse(misuse).id in my_misuse_ids:
                    my_misuses.append(Misuse(misuse))

            self._MISUSES = my_misuses

        return self._MISUSES

    @property
    def patterns(self) -> Set[Pattern]:
        if not self._PATTERNS:
            self._PATTERNS = set()
            for misuse in self.misuses:
                self._PATTERNS.update(misuse.patterns)

        return self._PATTERNS

    @property
    def revision(self) -> Optional[str]:
        if getattr(self, '_REVISION', None) is None:
            self._REVISION = self._yaml.get('revision')
        return self._REVISION

    @property
    def additional_compile_sources(self) -> str:
        return join(self._path, 'compile')
