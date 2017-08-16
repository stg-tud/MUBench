import logging

from typing import Dict, Optional, Any

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from tasks.project_version_misuse_task import ProjectVersionMisuseTask


class DatasetCheck(ProjectVersionMisuseTask):
    def __init__(self):
        self.logger = logging.getLogger("datasetcheck")
        super().__init__()

    def process_project(self, project: Project):
        yaml_path = "{}/project.yml".format(project.id)

        if "name" not in project._YAML:
            self._missing_key("name", yaml_path)

        if "repository" not in project._YAML:
            self._missing_key("repository", yaml_path)
        else:
            if "type" not in project._YAML["repository"]:
                self._missing_key("repository.type", yaml_path)
            if "url" not in project._YAML["repository"]:
                self._missing_key("repository.url", yaml_path)

        return super().process_project(project)

    def process_project_version(self, project: Project, version: ProjectVersion):
        return super().process_project_version(project, version)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        return self.ok()

    def _missing_key(self, tag: str, file_path: str):
        self.logger.warning('Missing "{}" in "{}".'.format(tag, file_path))
