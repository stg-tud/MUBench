import csv
import os
import traceback

import sys
from typing import List

from boa.BOA import BOA, GitHubProject
from buildtools.maven import Project
from utils.io import write_yamls
from utils.shell import CommandFailedError

MUBENCH_ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
CHECKOUTS_PATH = os.path.join(MUBENCH_ROOT_PATH, "checkouts", "_examples")
INDEX_PATH = os.path.join(CHECKOUTS_PATH, "index.csv")
SUBTYPES_PATH = os.path.join(CHECKOUTS_PATH, "subtype.csv")

_SUBTYPES = {}

username = sys.argv[1]
password = sys.argv[2]


def _prepare_example_projects(projects: List[GitHubProject], metadata_path: str):
    data = []
    for project in projects:
        print("[INFO] Preparing example project {}".format(project))

        checkout = project.get_checkout(CHECKOUTS_PATH)
        if not checkout.exists():
            try:
                print("[INFO]   Checking out...")
                checkout.create()
            except CommandFailedError as error:
                print("[WARN] Checkout failed: {}".format(error))
                checkout.delete()
                continue

        data.append({
            "id": project.id,
            "url": project.repository_url,
            "path": os.path.relpath(checkout.checkout_dir, MUBENCH_ROOT_PATH),
            "source_paths": Project(checkout.checkout_dir).get_sources_paths()
        })

    write_yamls(data, metadata_path)


def _get_subtypes(target_type):
    if not _SUBTYPES:
        with open(SUBTYPES_PATH) as subtypes_file:
            for subtypes_entry in subtypes_file.readlines():
                _SUBTYPES[subtypes_entry[0]] = subtypes_entry[1:]

    return _SUBTYPES.get(target_type, [])


with open(INDEX_PATH) as index:
    boa = BOA(username, password)
    for row in csv.reader(index, delimiter="\t"):
        project_id = row[0]
        version_id = row[1]
        target_type = row[2]
        try:
            print("[INFO] Preparing examples for {}.{} (target type: {})".format(project_id, version_id, target_type))
            projects = boa.query_projects_with_type_usages(target_type, _get_subtypes(target_type))
            target_example_file = os.path.join(CHECKOUTS_PATH, target_type + ".yml")
            _prepare_example_projects(projects, target_example_file)
        except UserWarning as warning:
            print("[WARN] {}".format(warning))
        except Exception as error:
            print("[ERROR] {}".format(error))
            traceback.print_exc(file=sys.stdout)
