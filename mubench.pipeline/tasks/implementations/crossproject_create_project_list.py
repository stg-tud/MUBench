import csv
import logging
import os
from os.path import join

from utils.io import open_yamls_if_exists, write_yaml
from utils.shell import Shell


class CrossProjectCreateProjectListTask:
    def __init__(self, root_path: str, index_file: str, base_checkout_path: str):
        self.root_path = root_path
        self.index_file = index_file
        self.base_checkout_path = base_checkout_path

    def run(self):
        logger = logging.getLogger("tasks.cross_project_create_project_list")
        example_projects_by_API = {}
        with open(self.index_file) as index:
            for row in csv.reader(index, delimiter="\t"):
                # skip blank lines, e.g., on trailing newline
                if not row:
                    continue

                target_type = row[6]
                try:
                    if target_type not in example_projects_by_API:
                        logger.info("Preparing examples for type: %s...", target_type)
                        target_example_file = os.path.join(self.base_checkout_path, target_type + ".yml")
                        example_projects = {}
                        with open_yamls_if_exists(target_example_file) as projects:
                            for project in projects:
                                hash = Shell.exec("cd \"{}\"; git rev-parse HEAD".format(join(self.root_path, project["path"])))
                                example_projects[project["url"]] = hash.strip()
                        example_projects_by_API[target_type] = example_projects
                except Exception as error:
                    logger.exception("failed", exc_info=error)

        write_yaml(example_projects_by_API, join(self.base_checkout_path, "example_projects_by_API.yml"))
