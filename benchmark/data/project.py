import yaml
from os import listdir
from os.path import join, exists, isdir, basename
from typing import List, Dict, Any, Optional

from benchmark.data.project_checkout import ProjectCheckout, GitProjectCheckout, SVNProjectCheckout, \
    LocalProjectCheckout
from benchmark.data.project_compile import ProjectCompile
from benchmark.data.project_version import ProjectVersion


# noinspection PyAttributeOutsideInit


class Project:
    PROJECT_FILE = 'project.yml'
    VERSIONS_DIR = "versions"

    class Repository:
        def __init__(self, vcstype: Optional[str], url: Optional[str]):
            self.vcstype = vcstype  # type: Optional[str]
            self.url = url  # type: Optional[str]

    def __init__(self, path: str, id: str):
        self._path = join(path, id)
        self._versions_path = join(self._path, Project.VERSIONS_DIR)  # type: str
        self._project_file = join(self._path, Project.PROJECT_FILE)  # type: str
        self._YAML = {}
        self._VERSIONS = []

    @staticmethod
    def is_project(path: str) -> bool:
        return exists(join(path, Project.PROJECT_FILE))

    @property
    def _yaml(self) -> Dict[str, Any]:
        if not self._YAML:
            with open(self._project_file) as project_file:
                project_yml = yaml.load(project_file)
            self._YAML = project_yml
        return self._YAML

    @property
    def id(self):
        return basename(self._path)

    @property
    def name(self) -> Optional[str]:
        return self._yaml.get("name", None)

    @property
    def repository(self) -> Repository:
        if getattr(self, '_REPOSITORY', None) is None:
            repository = self._yaml.get("repository", None)
            if repository is None:
                raise ValueError("Repository not defined")
            repository_type = repository.get("type", None)
            repository_url = repository.get("url", None)
            self._REPOSITORY = Project.Repository(repository_type, repository_url)
        return self._REPOSITORY

    def get_checkout(self, version: ProjectVersion, base_path: str) -> ProjectCheckout:
        repository = self.repository
        if repository.vcstype == "git":
            url = repository.url
            revision = version.revision + "~1"
            return GitProjectCheckout(url, base_path, self.id, version.id, revision)
        elif repository.vcstype == "svn":
            url = repository.url
            revision = str(int(version.revision) - 1)
            return SVNProjectCheckout(url, base_path, self.id, version.id, revision)
        elif repository.vcstype == "synthetic":
            url = join(self._path, Project.VERSIONS_DIR, "0", "compile")
            return LocalProjectCheckout(url, base_path, self.id)
        else:
            raise ValueError("unknown repository type: {}".format(repository.vcstype))

    @property
    def versions(self) -> List[ProjectVersion]:
        if not self._VERSIONS:
            if exists(self._versions_path):
                self._VERSIONS = [ProjectVersion(join(self._versions_path, subdir)) for subdir in
                                  listdir(self._versions_path) if
                                  ProjectVersion.is_project_version(join(self._versions_path, subdir))]
        return self._VERSIONS

    def get_compile(self, version: ProjectVersion, base_path: str) -> ProjectCompile:
        if version:
            base_path = join(base_path, self.id, version.id)
        else:
            base_path = join(base_path, self.id)
        return ProjectCompile(base_path)

    def __str__(self):
        return "project '{}'".format(self.id)

    def __eq__(self, other):
        return isinstance(other, Project) and self._path == other._path
