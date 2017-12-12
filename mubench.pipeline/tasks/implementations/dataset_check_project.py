import logging

from data.project import Project


class ProjectCheckTask:
    def __init__(self):
        self.logger = logging.getLogger("datasetcheck.project")

    def run(self, project: Project):
        self._check_required_keys_in_project_yaml(project)

    def _check_required_keys_in_project_yaml(self, project: Project):
        yaml_path = "{}/project.yml".format(project.id)
        project_yaml = project._yaml

        if "name" not in project_yaml:
            self._report_missing_key("name", yaml_path)

        if "repository" not in project_yaml:
            self._report_missing_key("repository", yaml_path)
        else:
            if "type" not in project_yaml["repository"]:
                self._report_missing_key("repository.type", yaml_path)
            if "url" not in project_yaml["repository"] and not project.repository.vcstype == 'synthetic':
                self._report_missing_key("repository.url", yaml_path)

    def _report_missing_key(self, tag: str, file_path: str):
        self.logger.warning('Missing "{}" in "{}".'.format(tag, file_path))
