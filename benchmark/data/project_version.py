import yaml
from os import listdir
from os.path import exists, pardir, isdir, realpath, basename
from os.path import join
from typing import List, Optional, Any, Dict

from benchmark.data.build_config import BuildConfig
from benchmark.data.misuse import Misuse


# noinspection PyAttributeOutsideInit
class ProjectVersion:
    VERSION_FILE = 'version.yml'

    def __init__(self, path: str):
        self._path = path  # type: str
        self._version_file = join(self._path, ProjectVersion.VERSION_FILE)  # type: str
        self._misuses_dir = realpath(join(self._path, pardir, pardir, 'misuses'))  # type: str

    @staticmethod
    def validate(path: str) -> bool:
        return exists(join(path, ProjectVersion.VERSION_FILE))

    @property
    def _yaml(self) -> Dict[str, Any]:
        if getattr(self, '_YAML', None) is None:
            with open(self._version_file) as stream:
                version_yml = yaml.load(stream)
            self._YAML = version_yml
        return self._YAML

    @property
    def build_config(self) -> BuildConfig:
        build = {"src": "", "commands": [], "classes": ""}
        build.update(self._yaml.get("build", {}))
        src = build.get("src")
        commands = build.get("commands")
        classes = build.get("classes")
        return BuildConfig(src, commands, classes)

    @property
    def misuses(self) -> List[Misuse]:
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

        return my_misuses

    @property
    def revision(self) -> Optional[str]:
        return self._yaml.get('revision')

    @property
    def additional_compile_sources(self) -> str:
        return join(self._path, 'compile')

    def __str__(self):
        return basename(self._path)
