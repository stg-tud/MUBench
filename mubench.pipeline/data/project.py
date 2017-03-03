from os import listdir
from os.path import join, exists
from typing import List, Dict, Any, Optional

import yaml

from data.project_version import ProjectVersion
from data.repository import Repository


class Project:
    PROJECT_FILE = 'project.yml'
    VERSIONS_DIR = "versions"
    MISUSES_DIR = "misuses"

    def __init__(self, base_path: str, id: str):
        self._base_path = base_path
        self.id = id
        self.path = join(base_path, id)
        self._versions_path = join(self.path, Project.VERSIONS_DIR)  # type: str
        self._project_file = join(self.path, Project.PROJECT_FILE)  # type: str
        self._YAML = {}
        self._VERSIONS = []
        self._REPOSITORY = None

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
    def name(self) -> Optional[str]:
        return self._yaml.get("name", None)

    @property
    def repository(self) -> Repository:
        if not self._REPOSITORY:
            repository = self._yaml.get("repository", None)
            if repository is None:
                raise ValueError("Repository not defined")
            repository_type = repository.get("type", None)
            repository_url = repository.get("url", None)
            self._REPOSITORY = Repository(repository_type, repository_url)
        return self._REPOSITORY

    @property
    def versions(self) -> List[ProjectVersion]:
        if not self._VERSIONS:
            if exists(self._versions_path):
                self._VERSIONS = [ProjectVersion(self._base_path, self.id, subdir) for subdir in
                                  listdir(self._versions_path) if
                                  ProjectVersion.is_project_version(join(self._versions_path, subdir))]
        return self._VERSIONS

    def __str__(self):
        return "project '{}'".format(self.id)

    def __eq__(self, other):
        return isinstance(other, Project) and self.path == other.path
