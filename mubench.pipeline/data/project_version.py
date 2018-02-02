from os.path import exists
from os.path import join
from typing import List, Optional, Any, Dict, Set

from data.misuse import Misuse, Pattern
from data.project_checkout import ProjectCheckout, GitProjectCheckout, SVNProjectCheckout, \
    SyntheticProjectCheckout, ZipProjectCheckout
from data.version_compile import VersionCompile
from utils.io import read_yaml


class ProjectVersion:
    VERSION_FILE = 'version.yml'

    VARS_CLASSES = {
                '$gradle.default.classes': "build/classes/java/main/",
                '$mvn.default.classes': "target/classes/",
                '$mvn.default.test-classes': "target/test-classes/"
            }

    def __init__(self, base_path: str, project_id: str, version_id: str):
        self._base_path = base_path
        self.version_id = version_id
        self.project_id = project_id
        self.id = "{}.{}".format(project_id, version_id)

        from data.project import Project
        self.__project = Project(base_path, project_id)

        self.path = join(self.__project.path, Project.VERSIONS_DIR, version_id)
        self._version_file = join(self.path, ProjectVersion.VERSION_FILE)  # type: str
        self._misuses_dir = join(self.__project.path, Project.MISUSES_DIR)  # type: str
        self._YAML = None
        self._MISUSES = None
        self._PATTERNS = None

    @staticmethod
    def is_project_version(path: str) -> bool:
        return exists(join(path, ProjectVersion.VERSION_FILE))

    @property
    def _yaml(self) -> Dict[str, Any]:
        if self._YAML is None:
            self._YAML = read_yaml(self._version_file)
        return self._YAML

    def get_checkout(self, base_path: str) -> ProjectCheckout:
        repository = self.__project.repository
        if repository.vcstype == "git":
            url = repository.url
            return GitProjectCheckout(self.__project.id, self.version_id, url, self.revision, base_path)
        elif repository.vcstype == "svn":
            url = repository.url
            return SVNProjectCheckout(self.__project.id, self.version_id, url, self.revision, base_path)
        elif repository.vcstype == "synthetic":
            return SyntheticProjectCheckout(self.__project.id, self.version_id, self.path, base_path)
        elif repository.vcstype == "zip":
            return ZipProjectCheckout(self.__project.id, self.version_id, self.revision, self._yaml["md5"], base_path)
        else:
            raise ValueError("unknown repository type: {}".format(repository.vcstype))

    def get_compile(self, base_path: str) -> VersionCompile:
        return VersionCompile(join(base_path, self.project_id, self.version_id), self.source_dirs, self.classes_dirs)

    @property
    def __compile_config(self):
        compile = {"src": [""], "commands": [], "classes": [""]}
        compile.update(self._yaml.get("build", {}))

        src = compile["src"]
        if type(src) == str:
            compile["src"] = [src]
        classes = compile["classes"]
        if type(classes) == str:
            compile["classes"] = [classes]

        for key, value in self.VARS_CLASSES.items():
            compile["classes"] = [classes.replace(key, value) for classes in compile["classes"]]

        return compile

    @property
    def source_dirs(self) -> List[str]:
        return self.__compile_config["src"]

    @property
    def compile_commands(self):
        return self.__compile_config["commands"]

    @property
    def classes_dirs(self) -> List[str]:
        return self.__compile_config["classes"]

    @property
    def misuses(self) -> List[Misuse]:
        if not self._MISUSES:
            misuse_ids = self._yaml.get("misuses", []) or []
            self._MISUSES = [Misuse(self._base_path, self.__project.id, self.version_id, misuse_id)
                             for misuse_id in misuse_ids
                             if Misuse.is_misuse(join(self._misuses_dir, misuse_id))]

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
        return join(self.path, 'compile')

    @property
    def is_compilable(self) -> bool:
        return self.source_dirs and self.compile_commands and self.classes_dirs

    def __str__(self):
        return "project '{}' version {}".format(self.project_id, self.version_id)

    def __eq__(self, other):
        return isinstance(other, ProjectVersion) and self._version_file == other._version_file
