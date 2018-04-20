import csv
import logging
import os
from os.path import exists, join
from typing import List

from boa.BOA import BOA
from buildtools.maven import Project
from utils.io import write_yamls, write_yaml, is_empty
from utils.shell import CommandFailedError


class CrossProjectPrepareTask:
    def __init__(self, root_path: str, checkouts_base_path: str, index_file: str, timestamp: int,
                 max_project_sample_size: int, boa_user: str, boa_password: str):
        self.root_path = root_path
        self.checkouts_base_path = checkouts_base_path
        self.project_checkouts_path = join(checkouts_base_path, "checkouts")
        self.boa_results_path = join(checkouts_base_path, "boa-results")
        self.subtypes_path = os.path.join(checkouts_base_path, "subtypes.csv")
        self.index_file = index_file
        self.timestamp = timestamp
        self.max_project_sample_size = max_project_sample_size
        self.boa_user = boa_user
        self.boa_password = boa_password

        self._subtypes = {}

    def run(self):
        logger = logging.getLogger("tasks.cross_project_prepare")
        with open(self.index_file) as index:
            boa = BOA(self.boa_user, self.boa_password, self.boa_results_path)
            for row in csv.reader(index, delimiter="\t"):
                # skip blank lines, e.g., on trailing newline
                if not row:
                    continue

                project_id = row[0]
                version_id = row[1]
                target_types = sorted(row[6:])
                try:
                    target_example_file = os.path.join(self.project_checkouts_path, "-".join(sorted(target_types)) + ".yml")
                    if not exists(target_example_file):
                        logger.info("Preparing examples for %s.%s (type(s): %s)...", project_id, version_id,
                                    target_types)
                        self._prepare_example_projects(target_types, boa, target_example_file)
                    elif is_empty(target_example_file):
                        logger.info("No example projects for %s.%s (type(s): %s)", project_id, version_id, target_types)
                    else:
                        logger.info("Already prepared examples for %s.%s (type(s): %s)", project_id, version_id,
                                    target_types)
                except Exception as error:
                    logger.exception("failed", exc_info=error)

    def _prepare_example_projects(self, target_types: List, boa: BOA, metadata_path: str):
        logger = logging.getLogger("tasks.cross_project_prepare")
        data = []
        for type_combination in self._create_type_combinations(target_types):
            projects = boa.query_projects_with_type_usages(target_types, type_combination)
            for project in projects:
                checkout = project.get_checkout(self.checkouts_base_path)
                if not checkout.exists():
                    try:
                        logger.info("  Checking out %r...", str(project))
                        checkout.clone()
                    except CommandFailedError as error:
                        logger.warning("    Checkout failed: %r", error)
                        checkout.delete()
                        continue
                else:
                    logger.info("  Already checked out %r.", str(project))

                try:
                    project_entry = {"id": project.id, "url": project.repository_url,
                                     "path": os.path.relpath(checkout.path, self.root_path),
                                     "source_paths": Project(checkout.path).get_sources_paths(),
                                     "checkout_timestamp": self.timestamp}
                    write_yaml(project_entry)  # check for encoding problems
                    data.append(project_entry)
                except UnicodeEncodeError:
                    logger.warning("    Illegal characters in project data.")

                if len(data) >= self.max_project_sample_size:
                    logger.warning("  Stopping after %r of %r example projects.", self.max_project_sample_size,
                                   len(projects))
                    write_yamls(data, metadata_path)
                    return

        write_yamls(data, metadata_path)

    def _get_subtypes(self, target_type):
        if not self._subtypes and exists(self.subtypes_path):
            with open(self.subtypes_path) as subtypes_file:
                for subtypes_row in csv.reader(subtypes_file, delimiter="\t"):
                    self._subtypes[subtypes_row[0]] = subtypes_row[1:]

        all_subtypes = self._subtypes.get(target_type, [])
        subtypes_sample = [subtype for subtype in all_subtypes if "sun." not in subtype]  # filter Sun-specific types
        return subtypes_sample

    def _get_type_and_subtypes_list(self, target_type):
        return [target_type] + self._get_subtypes(target_type)

    def _create_type_combinations(self, target_types: List):
        if len(target_types) == 1:
            return ([type_] for type_ in self._get_type_and_subtypes_list(target_types[0]))
        else:
            return ([target_type] + tail
                    for target_type in self._get_type_and_subtypes_list(target_types[0])
                    for tail in self._create_type_combinations(target_types[1:]))
