import logging
from os import listdir
from os.path import join, isdir, basename, exists
from typing import Dict, List

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from data.snippets import get_snippets

VALID_VIOLATION_TYPES = [
        'missing/call',
        'missing/condition/null_check',
        'missing/condition/synchronization',
        'missing/condition/value_or_state',
        'missing/condition/context',
        'missing/iteration',
        'missing/exception_handling',
        'superfluous/call',
        'superfluous/condition/null_check',
        'superfluous/condition/synchronization',
        'superfluous/condition/value_or_state',
        'superfluous/condition/context',
        'superfluous/iteration',
        'superfluous/exception_handling',
        'misplaced/call',
    ]


class DatasetCheckTask:
    def __init__(self, datasets: Dict[str, List[str]], checkout_base_path: str, data_base_path: str):
        super().__init__()
        self.logger = logging.getLogger("tasks.datasetcheck")
        self.datasets = datasets
        self.checkout_base_path = checkout_base_path
        self.misuses_not_listed_in_any_version = []
        self.registered_entries = set()
        self.misuses_not_listed_in_any_version = self._get_all_misuses(data_base_path)

    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
        self.check_project(project)
        self.check_project_version(project, version)
        self.check_project_version_misuse(project, version, misuse)
        return []

    def check_project(self, project: Project):
        self.logger = logging.getLogger("datasetcheck.project")
        self._register_entry(project, project.id)
        self._check_required_keys_in_project_yaml(project)

    def check_project_version(self, project: Project, version: ProjectVersion):
        self.logger = logging.getLogger("datasetcheck.project.version")
        self._register_entry(project, version.id)
        self._check_required_keys_in_version_yaml(project, version)
        self._check_misuses_listed_in_version_exist(project, version)

    def check_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        self.logger = logging.getLogger("datasetcheck.project.version.misuse")
        self._register_entry(project, misuse.id)
        self._register_misuse_is_linked_from_version(misuse.id)
        self._check_required_keys_in_misuse_yaml(project, version, misuse)
        self._check_misuse_location_exists(project, version, misuse)
        self._check_violation_types(project, misuse)

    def end(self):
        self.logger = logging.getLogger("datasetcheck.misuse")
        self._report_misuses_not_listed_in_any_version()
        self.logger = logging.getLogger("datasetcheck")
        self._report_unknown_dataset_entries()

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
            if "url" not in project_yaml["repository"] and not _is_synthetic(project):
                self._report_missing_key("repository.url", yaml_path)

    def _check_required_keys_in_version_yaml(self, project: Project, version: ProjectVersion):
        yaml_path = "{}/versions/{}/version.yml".format(project.id, version.version_id)
        version_yaml = version._yaml

        if "revision" not in version_yaml and not _is_synthetic(project):
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

    def _check_required_keys_in_misuse_yaml(self, project: Project, version: ProjectVersion, misuse: Misuse):
        yaml_path = "{}/misuses/{}/misuse.yml".format(project.id, misuse.misuse_id)
        misuse_yaml = misuse._yaml

        if "location" not in misuse_yaml:
            self._report_missing_key("location", yaml_path)
        else:
            location = misuse_yaml["location"]
            if "file" not in location:
                self._report_missing_key("location.file", yaml_path)
            if "method" not in location:
                self._report_missing_key("location.method", yaml_path)

        if "api" not in misuse_yaml:
            self._report_missing_key("api", yaml_path)

        if not misuse_yaml.get("characteristics", None):
            self._report_missing_key("characteristics", yaml_path)

        if not misuse_yaml.get("description", None):
            self._report_missing_key("description", yaml_path)

        if not _is_synthetic(project):
            if "fix" not in misuse_yaml:
                self._report_missing_key("fix", yaml_path)
            else:
                fix = misuse_yaml["fix"]
                if "commit" not in fix:
                    self._report_missing_key("fix.commit", yaml_path)
                if "revision" not in fix:
                    self._report_missing_key("fix.revision", yaml_path)

            if "internal" not in misuse_yaml:
                self._report_missing_key("internal", yaml_path)

            if "report" not in misuse_yaml:
                self._report_missing_key("report", yaml_path)

            if "source" not in misuse_yaml:
                self._report_missing_key("source", yaml_path)
            else:
                source = misuse_yaml["source"]
                if "name" not in source:
                    self._report_missing_key("source.name", yaml_path)
                if "url" not in source:
                    self._report_missing_key("source.url", yaml_path)

    def _check_misuses_listed_in_version_exist(self, project: Project, version: ProjectVersion):
        for misuse_id in version._yaml.get("misuses", []) or []:
            if not Misuse.is_misuse(join(project.path, project.MISUSES_DIR, misuse_id)):
                self._report_unknown_misuse(version.id, misuse_id)

    def _check_misuse_location_exists(self, project: Project, version: ProjectVersion, misuse: Misuse):
        if "location" in misuse._yaml:
            location = misuse.location
            if location.file and location.method:
                checkout = version.get_checkout(self.checkout_base_path)
                if not checkout.exists():
                    self.logger.debug(
                            'Skipping location check for "{}": requires checkout of "{}".'.format(
                                misuse.id, version.id))
                else:
                    source_base_path = join(checkout.checkout_dir, version.source_dir)
                    if not self._location_exists(source_base_path, location.file, location.method):
                        self._report_cannot_find_location(str(location), "{}/misuses/{}/misuse.yml".format(project.id, misuse.misuse_id))

    def _location_exists(self, source_base_path, file_, method) -> bool:
        try:
            snippets = get_snippets(source_base_path, file_, method)
        except:
            return False
        else:
            return len(snippets) > 0

    def _check_violation_types(self, project: Project, misuse: Misuse):
        violation_types = misuse._yaml.get("characteristics", [])
        for violation_type in violation_types:
            if violation_type not in VALID_VIOLATION_TYPES:
                file_path = "{}/misuses/{}/misuse.yml".format(project.id, misuse.misuse_id)
                self._report_invalid_violation_type(violation_type, file_path)

    def _register_entry(self, project: Project, id_: str):
        for dataset, entries in self.datasets.items():
            if id_ in entries:
                entries.remove(id_)

        if not id_ in self.registered_entries:
            self.registered_entries.add(id_)
        else:
            if not _is_synthetic(project):
                self._report_id_conflict(id_)

    def _register_misuse_is_linked_from_version(self, misuse: str):
        if misuse in self.misuses_not_listed_in_any_version:
            self.misuses_not_listed_in_any_version.remove(misuse)

    def _report_unknown_dataset_entries(self):
        for dataset, entries in self.datasets.items():
            for entry in entries:
                self._report_unknown_dataset_entry(dataset, entry)

    def _report_misuses_not_listed_in_any_version(self):
        for misuse in self.misuses_not_listed_in_any_version:
            self._report_misuse_not_listed(misuse)

    def _report_missing_key(self, tag: str, file_path: str):
        self.logger.warning('Missing "{}" in "{}".'.format(tag, file_path))

    def _report_id_conflict(self, conflicting_id: str):
        self.logger.warning('ID "{}" is used for multiple data entries.'.format(conflicting_id))

    def _report_unknown_misuse(self, version_id: str, unknown_misuse_id: str):
        self.logger.warning('Unknown misuse "{}" in "{}".'.format(unknown_misuse_id, version_id))

    def _report_cannot_find_location(self, location: str, misuse_yaml_path: str):
        self.logger.warning('Cannot find "{}" listed in "{}".'.format(location, misuse_yaml_path))

    def _report_unknown_dataset_entry(self, dataset: str, entry: str):
        self.logger.warning('Unknown dataset entry "{}" in dataset "{}".'.format(entry, dataset))

    def _report_misuse_not_listed(self, misuse_id: str):
        self.logger.warning('Misuse "{}" is not listed in any versions.'.format(misuse_id))

    def _report_invalid_violation_type(self, violation_type: str, file_path: str):
        self.logger.warning('Invalid violation type "{}" in "{}"'.format(violation_type, file_path))

    def _get_all_misuses(self, data_base_path: str) -> List[str]:
        misuses = []

        project_dirs = [join(data_base_path, subdir) for subdir in listdir(data_base_path) if isdir(join(data_base_path, subdir))]
        for project_dir in project_dirs:
            misuses_dir = join(project_dir, "misuses")
            if not exists(misuses_dir):
                continue

            misuse_ids = [subdir for subdir in listdir(misuses_dir) if isdir(join(misuses_dir, subdir))]
            misuse_ids = ["{}.{}".format(basename(project_dir), misuse) for misuse in misuse_ids]
            misuses.extend(misuse_ids)

        return misuses


def _is_synthetic(project: Project) -> bool:
    return project._yaml.get("repository", {}).get("type", '') == "synthetic"
