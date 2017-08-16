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
        yaml_path = "{}/{}/version.yml".format(project.id, version.version_id)

        if "revision" not in version._YAML:
            self._missing_key("revision", yaml_path)

        if "build" not in version._YAML:
            self._missing_key("build", yaml_path)
        else:
            build = version._YAML["build"]
            if "classes" not in build:
                self._missing_key("build.classes", yaml_path)
            if not build.get("commands", None):
                self._missing_key("build.commands", yaml_path)
            if "src" not in build:
                self._missing_key("build.src", yaml_path)

        if not version._YAML.get("misuses", None):
            self._missing_key("misuses", yaml_path)

        return super().process_project_version(project, version)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        return self.ok()

    def _missing_key(self, tag: str, file_path: str):
        self.logger.warning('Missing "{}" in "{}".'.format(tag, file_path))
