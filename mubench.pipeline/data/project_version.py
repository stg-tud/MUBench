import logging
from os.path import exists
from os.path import join
from typing import List, Optional, Any, Dict, Set

import yaml

from data.misuse import Misuse, Pattern
from data.project_checkout import ProjectCheckout, GitProjectCheckout, SVNProjectCheckout, \
    SyntheticProjectCheckout, ZipProjectCheckout
from data.project_compile import ProjectCompile


class ProjectVersion:
    VERSION_FILE = 'version.yml'

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
            with open(self._version_file) as stream:
                version_yml = yaml.load(stream)
            self._YAML = version_yml
        return self._YAML

    def get_checkout(self, base_path: str) -> ProjectCheckout:
        repository = self.__project.repository
        if repository.vcstype == "git":
            url = repository.url
            return GitProjectCheckout(url, base_path, self.__project.id, self.version_id, self.revision)
        elif repository.vcstype == "svn":
            url = repository.url
            return SVNProjectCheckout(url, base_path, self.__project.id, self.version_id, self.revision)
        elif repository.vcstype == "synthetic":
            return SyntheticProjectCheckout(base_path, self.__project.id, self.version_id)
        elif repository.vcstype == "zip":
            return ZipProjectCheckout(self.revision, self._yaml["md5"], base_path, self.__project.id, self.version_id)
        else:
            raise ValueError("unknown repository type: {}".format(repository.vcstype))

    def get_compile(self, base_path: str) -> ProjectCompile:
        return ProjectCompile(join(base_path, self.project_id, self.version_id), self.misuses)

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
            misuse_ids = self._yaml.get("misuses", []) or []
            if not misuse_ids:
                logging.getLogger("version").warning("!! %s has no misuses!", self)
            self._MISUSES = [Misuse(self._base_path, self.__project.id, misuse_id) for misuse_id in misuse_ids
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

    def __str__(self):
        return "project '{}' version {}".format(self.project_id, self.version_id)

    def __eq__(self, other):
        return isinstance(other, ProjectVersion) and self._version_file == other._version_file
