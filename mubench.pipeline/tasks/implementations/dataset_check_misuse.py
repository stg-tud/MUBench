import logging
from os import listdir, path
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


def _get_all_misuses(data_base_path: str) -> List[str]:
    misuses = []

    project_dirs = [join(data_base_path, subdir) for subdir in
                    listdir(data_base_path) if isdir(join(data_base_path, subdir))]
    for project_dir in project_dirs:
        misuses_dir = join(project_dir, "misuses")
        if not exists(misuses_dir):
            continue

        misuse_ids = [subdir for subdir in listdir(misuses_dir) if isdir(join(misuses_dir, subdir))]
        misuse_ids = ["{}.{}".format(basename(project_dir), misuse) for misuse in misuse_ids]
        misuses.extend(misuse_ids)

    return misuses


class MisuseCheckTask:
    def __init__(self, datasets: Dict[str, List[str]], checkout_base_path: str, data_base_path: str):
        super().__init__()
        self.logger = logging.getLogger("tasks.datasetcheck")
        self.datasets = datasets
        self.checkout_base_path = checkout_base_path
        self.data_base_path = data_base_path
        self.registered_entries = set()
        self.misuses_not_listed_in_any_version = _get_all_misuses(data_base_path)
        self._report_invalid_dataset_entries()
        self._check_for_conflicting_dataset_names(datasets.keys())

    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
        self.logger = logging.getLogger("datasetcheck.project.version.misuse")
        self._register_existing_dataset_entry(misuse.id)
        self._register_misuse_is_linked_from_version(project.id, misuse.misuse_id)
        self._check_required_keys_in_misuse_yaml(project, misuse)
        self._check_misuse_location_exists(version, misuse)
        self._check_violation_types(misuse)

    def end(self):
        self.logger = logging.getLogger("datasetcheck.misuse")
        self._report_misuses_not_listed_in_any_version()
        self.logger = logging.getLogger("datasetcheck")
        self._report_unknown_dataset_entries()

    def _check_required_keys_in_misuse_yaml(self, project: Project, misuse: Misuse):
        yaml_path = self._get_rel_misuse_file_path(misuse)
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

        if not project.repository.vcstype == "synthetic":
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

    def _get_rel_misuse_file_path(self, misuse):
        return path.relpath(misuse.misuse_file, self.data_base_path)

    def _check_misuse_location_exists(self, version: ProjectVersion, misuse: Misuse):
        if "location" in misuse._yaml:
            location = misuse.location
            if location.file and location.method:
                checkout = version.get_checkout(self.checkout_base_path)
                if not checkout or not checkout.exists():
                    self.logger.debug(
                        'Skipping location check for "{}": requires checkout of "{}".'.format(
                            misuse.id, version.id))
                else:
                    source_base_paths = [join(checkout.base_path, src_dir) for src_dir in version.source_dirs]
                    if not self._location_exists(source_base_paths, location.file, location.method):
                        self._report_cannot_find_location(str(location), self._get_rel_misuse_file_path(misuse))

    @staticmethod
    def _location_exists(source_base_paths, file_, method) -> bool:
        return len(get_snippets(source_base_paths, file_, method)) > 0

    def _check_violation_types(self, misuse: Misuse):
        violation_types = misuse._yaml.get("characteristics", [])
        for violation_type in violation_types:
            if violation_type not in VALID_VIOLATION_TYPES:
                file_path = self._get_rel_misuse_file_path(misuse)
                self._report_invalid_violation_type(violation_type, file_path)

    def _register_existing_dataset_entry(self, misuse_id: str):
        for dataset, entries in self.datasets.items():
            if misuse_id in entries:
                entries.remove(misuse_id)

    def _register_misuse_is_linked_from_version(self, project_id: str, misuse_id: str):
        misuse = "{}.{}".format(project_id, misuse_id)
        if misuse in self.misuses_not_listed_in_any_version:
            self.misuses_not_listed_in_any_version.remove(misuse)

    def _report_invalid_dataset_entries(self):
        datasets_without_invalid_entries = dict()
        for dataset, entries in self.datasets.items():
            datasets_without_invalid_entries[dataset] = []
            for entry in entries:
                if len(entry.split('.')) < 3:
                    self._report_invalid_dataset_entry(dataset, entry)
                else:
                    datasets_without_invalid_entries[dataset].append(entry)
        self.datasets = datasets_without_invalid_entries

    def _check_for_conflicting_dataset_names(self, dataset_names: List[str]):
        seen_names = dict()
        for name in dataset_names:
            if name.lower() in seen_names:
                self._report_conflicting_dataset_name(seen_names[name.lower()], name)
            else:
                seen_names[name.lower()] = name

    def _report_conflicting_dataset_name(self, first_name: str, second_name: str):
        self.logger.warning('Conflicting dataset names "{}" and "{}". Dataset names are case insensitive!'.format(first_name, second_name))

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

    def _report_cannot_find_location(self, location: str, misuse_yaml_path: str):
        self.logger.warning('Cannot find "{}" listed in "{}".'.format(location, misuse_yaml_path))

    def _report_unknown_dataset_entry(self, dataset: str, entry: str):
        self.logger.warning('Unknown dataset entry "{}" in dataset "{}".'.format(entry, dataset))

    def _report_misuse_not_listed(self, misuse_id: str):
        self.logger.warning('Misuse "{}" is not listed in any versions.'.format(misuse_id))

    def _report_invalid_violation_type(self, violation_type: str, file_path: str):
        self.logger.warning('Invalid violation type "{}" in "{}"'.format(violation_type, file_path))

    def _report_invalid_dataset_entry(self, dataset: str, invalid_entry: str):
        self.logger.warning('Invalid dataset entry "{}" in "{}". '
                            'Entries must be "project.version.misuse".'.format(invalid_entry, dataset))
