from os import listdir
from os.path import exists, isdir
from os.path import join
from typing import List, Optional, Any, Dict, Set

import yaml

from benchmark.data.misuse import Misuse, Pattern
from benchmark.data.project_checkout import ProjectCheckout, GitProjectCheckout, SVNProjectCheckout, \
    LocalProjectCheckout
from benchmark.data.project_compile import ProjectCompile


class ProjectVersion:
    VERSION_FILE = 'version.yml'
    MISUSES_DIR = "misuses"

    def __init__(self, base_path: str, project_id: str, version_id: str):
        self.version_id = version_id
        self.project_id = project_id
        self.id = "{}.{}".format(project_id, version_id)

        from benchmark.data.project import Project
        self.__project = Project(base_path, project_id)

        self.path = join(self.__project.path, Project.VERSIONS_DIR, version_id)
        self._version_file = join(self.path, ProjectVersion.VERSION_FILE)  # type: str
        self._misuses_dir = join(self.__project.path, ProjectVersion.MISUSES_DIR)  # type: str
        self._YAML = None
        self._MISUSES = None
        self._PATTERNS = None

    @staticmethod
    def is_project_version(path: str) -> bool:
        return exists(join(path, ProjectVersion.VERSION_FILE))

    @property
    def _yaml(self) -> Dict[str, Any]:
        if self._YAML is None:
            with open(self._version_file) as stream:
                version_yml = yaml.load(stream)
            self._YAML = version_yml
        return self._YAML

    def get_checkout(self, base_path: str) -> ProjectCheckout:
        repository = self.__project.repository
        if repository.vcstype == "git":
            url = repository.url
            revision = self.revision + "~1"
            return GitProjectCheckout(url, base_path, self.__project.id, self.version_id, revision)
        elif repository.vcstype == "svn":
            url = repository.url
            revision = str(int(self.revision) - 1)
            return SVNProjectCheckout(url, base_path, self.__project.id, self.version_id, revision)
        elif repository.vcstype == "synthetic":
            from benchmark.data.project import Project
            url = join(self.path, "compile")
            return LocalProjectCheckout(url, base_path, self.__project.id)
        else:
            raise ValueError("unknown repository type: {}".format(repository.vcstype))

    def get_compile(self, base_path: str) -> ProjectCompile:
        return ProjectCompile(join(base_path, self.project_id, self.version_id))

    @property
    def __compile_config(self):
        compile = {"src": "", "commands": [], "classes": ""}
        compile.update(self._yaml.get("build", {}))
        return compile

    @property
    def source_dir(self):
        return self.__compile_config["src"]

    @property
    def compile_commands(self):
        return self.__compile_config["commands"]

    @property
    def classes_dir(self):
        return self.__compile_config["classes"]

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
        return join(self.path, 'compile')

    def __str__(self):
        return "project version '{}'".format(self.id)

    def __eq__(self, other):
        return isinstance(other, ProjectVersion) and self._version_file == other._version_file
