import logging
from os.path import join

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion


class VersionCheckTask:
    def __init__(self):
        self.logger = logging.getLogger("datasetcheck.project.version")

    def run(self, project: Project, version: ProjectVersion):
        self._check_required_keys_in_version_yaml(project, version)
        self._check_misuses_listed_in_version_exist(project, version)

    def _check_required_keys_in_version_yaml(self, project: Project, version: ProjectVersion):
        yaml_path = "{}/versions/{}/version.yml".format(project.id, version.version_id)
        version_yaml = version._yaml

        if "revision" not in version_yaml and not project.repository.vcstype == 'synthetic':
            self._report_missing_key("revision", yaml_path)

        if "build" not in version_yaml:
            self._report_missing_key("build", yaml_path)
        else:
            build = version_yaml["build"]
            if "classes" not in build:
                self._report_missing_key("build.classes", yaml_path)
            if not build.get("commands", None):
                self._report_missing_key("build.commands", yaml_path)
            if "src" not in build:
                self._report_missing_key("build.src", yaml_path)

        if not version_yaml.get("misuses", None):
            self._report_missing_key("misuses", yaml_path)

    def _check_misuses_listed_in_version_exist(self, project: Project, version: ProjectVersion):
        for misuse_id in version._yaml.get("misuses", []) or []:
            if not Misuse.is_misuse(join(project.path, project.MISUSES_DIR, misuse_id)):
                self._report_unknown_misuse(version.id, misuse_id)

    def _report_missing_key(self, tag: str, file_path: str):
        self.logger.warning('Missing "{}" in "{}".'.format(tag, file_path))

    def _report_unknown_misuse(self, version_id: str, unknown_misuse_id: str):
        self.logger.warning('Unknown misuse "{}" in "{}".'.format(unknown_misuse_id, version_id))


