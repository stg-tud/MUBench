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
        self._check_required_keys_in_project_yaml(project)

        return super().process_project(project)

    def _check_required_keys_in_project_yaml(self, project: Project):
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

    def process_project_version(self, project: Project, version: ProjectVersion):
        self._check_required_keys_in_version_yaml(project, version)

        return super().process_project_version(project, version)

    def _check_required_keys_in_version_yaml(self, project: Project, version: ProjectVersion):
        yaml_path = "{}/versions/{}/version.yml".format(project.id, version.version_id)

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

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        self._check_required_keys_in_misuse_yaml(project, version, misuse)

        return self.ok()

    def _check_required_keys_in_misuse_yaml(self, project: Project, version: ProjectVersion, misuse: Misuse):
        yaml_path = "{}/misuses/{}/misuse.yml".format(project.id, misuse.misuse_id)

        if "location" not in misuse._YAML:
            self._missing_key("location", yaml_path)
        else:
            location = misuse._YAML["location"]
            if "file" not in location:
                self._missing_key("location.file", yaml_path)
            if "method" not in location:
                self._missing_key("location.method", yaml_path)

        if "api" not in misuse._YAML:
            self._missing_key("api", yaml_path)

        if not misuse._YAML.get("characteristics", None):
            self._missing_key("characteristics", yaml_path)

        if not misuse._YAML.get("description", None):
            self._missing_key("description", yaml_path)

        if "fix" not in misuse._YAML:
            self._missing_key("fix", yaml_path)
        else:
            fix = misuse._YAML["fix"]
            if "commit" not in fix:
                self._missing_key("fix.commit", yaml_path)
            if "revision" not in fix:
                self._missing_key("fix.revision", yaml_path)

        if "internal" not in misuse._YAML:
            self._missing_key("internal", yaml_path)

        if "report" not in misuse._YAML:
            self._missing_key("report", yaml_path)

        if "source" not in misuse._YAML:
            self._missing_key("source", yaml_path)
        else:
            source = misuse._YAML["source"]
            if "name" not in source:
                self._missing_key("source.name", yaml_path)
            if "url" not in source:
                self._missing_key("source.url", yaml_path)

    def _missing_key(self, tag: str, file_path: str):
        self.logger.warning('Missing "{}" in "{}".'.format(tag, file_path))
