import calendar
import csv
import logging
import os
import sys
from datetime import datetime
from os.path import exists, join
from typing import List

from boa.BOA import BOA
from buildtools.maven import Project
from utils.io import write_yamls, write_yaml, is_empty
from utils.logging import IndentFormatter
from utils.shell import CommandFailedError

MUBENCH_ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
CHECKOUTS_PATH = os.path.join(MUBENCH_ROOT_PATH, "checkouts", "_examples")
BOA_RESULTS_PATH = join(CHECKOUTS_PATH, "_boa-results")
INDEX_PATH = os.path.join(CHECKOUTS_PATH, "index.csv")
SUBTYPES_PATH = os.path.join(CHECKOUTS_PATH, "subtypes.csv")
MAX_SUBTYPES_SAMPLE_SIZE = 25
MAX_PROJECT_SAMPLE_SIZE = 50

_SUBTYPES = {}

username = sys.argv[1]
password = sys.argv[2]

now = datetime.utcnow()
run_timestamp = calendar.timegm(now.timetuple())


def _get_subtypes(target_type):
    if not _SUBTYPES:
        with open(SUBTYPES_PATH) as subtypes_file:
            for subtypes_row in csv.reader(subtypes_file, delimiter="\t"):
                _SUBTYPES[subtypes_row[0]] = subtypes_row[1:]

    all_subtypes = _SUBTYPES.get(target_type, [])
    subtypes_sample = [subtype for subtype in all_subtypes if "sun." not in subtype]  # filter Sun-specific types
    return subtypes_sample


def _get_type_and_subtypes_list(target_type):
    return [target_type] + _get_subtypes(target_type)


def _create_type_combinations(target_types: List):
    if len(target_types) == 1:
        return [_get_type_and_subtypes_list(target_types[0])]
    else:
        return ([target_type] + tail
                for target_type in _get_type_and_subtypes_list(target_types[0])
                for tail in _create_type_combinations(target_types[1:]))


def _prepare_example_projects(target_types: List, boa: BOA, metadata_path: str):
    data = []
    for type_combination in _create_type_combinations(target_types):
        projects = boa.query_projects_with_type_usages(target_types, type_combination)
        for project in projects:
            checkout = project.get_checkout(CHECKOUTS_PATH)
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
                                 "path": os.path.relpath(checkout.path, MUBENCH_ROOT_PATH),
                                 "source_paths": Project(checkout.path).get_sources_paths(),
                                 "checkout_timestamp": run_timestamp}
                write_yaml(project_entry)
                data.append(project_entry)
            except UnicodeEncodeError:
                logger.warning("    Illegal characters in project data.")

            if len(data) >= MAX_PROJECT_SAMPLE_SIZE:
                logger.warning("  Stopping after %r of %r example projects.", MAX_PROJECT_SAMPLE_SIZE, len(projects))
                write_yamls(data, metadata_path)
                return

    write_yamls(data, metadata_path)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(IndentFormatter("%(asctime)s %(indent)s%(message)s"))
handler.setLevel(logging.INFO)
logger.addHandler(handler)
LOG_DIR = "logs"
if not exists(LOG_DIR):
    os.makedirs(LOG_DIR)
log_name = datetime.now().strftime("prepare_ex4_%Y%m%d_%H%M%S") + ".log"
handler = logging.FileHandler(join(LOG_DIR, log_name))
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


with open(INDEX_PATH) as index:
    boa = BOA(username, password, BOA_RESULTS_PATH)
    for row in csv.reader(index, delimiter="\t"):
        # skip blank lines, e.g., on trailing newline
        if not row:
            continue

        project_id = row[0]
        version_id = row[1]
        target_types = sorted(row[6:])
        try:
            target_example_file = os.path.join(CHECKOUTS_PATH, "-".join(sorted(target_types)) + ".yml")
            if not exists(target_example_file):
                logger.info("Preparing examples for %s.%s (type(s): %s)...", project_id, version_id, target_types)
                _prepare_example_projects(target_types, boa, target_example_file)
            elif is_empty(target_example_file):
                logger.info("No example projects for %s.%s (type(s): %s)", project_id, version_id, target_types)
            else:
                logger.info("Already prepared examples for %s.%s (type(s): %s)", project_id, version_id, target_types)
        except Exception as error:
            logger.exception("failed", exc_info=error)
