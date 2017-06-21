import csv
import os
import traceback

import sys

import logging
from datetime import datetime

from os.path import exists, join
from typing import List

from boa.BOA import BOA, GitHubProject
from buildtools.maven import Project
from utils.io import write_yamls
from utils.logging import IndentFormatter
from utils.shell import CommandFailedError

MUBENCH_ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
CHECKOUTS_PATH = os.path.join(MUBENCH_ROOT_PATH, "checkouts", "_examples")
INDEX_PATH = os.path.join(CHECKOUTS_PATH, "index.csv")
SUBTYPES_PATH = os.path.join(CHECKOUTS_PATH, "subtypes.csv")
MAX_SUBTYPES_SAMPLE_SIZE = 25
MAX_PROJECT_SAMPLE_SIZE = 50

_SUBTYPES = {}

username = sys.argv[1]
password = sys.argv[2]


def _prepare_example_projects(projects: List[GitHubProject], metadata_path: str):
    if len(projects) > MAX_PROJECT_SAMPLE_SIZE:
        logger.warning("Sampling %r of %r example projects...", MAX_PROJECT_SAMPLE_SIZE, len(projects))
        projects = projects[:MAX_PROJECT_SAMPLE_SIZE]

    data = []
    for project in projects:
        logger.info("Preparing example project %r", project.id)

        checkout = project.get_checkout(CHECKOUTS_PATH)
        if not checkout.exists():
            try:
                logger.info("  Checking out...")
                checkout.create()
            except CommandFailedError as error:
                logger.warning("Checkout failed: %r", error)
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
            for subtypes_row in csv.reader(subtypes_file, delimiter="\t"):
                _SUBTYPES[subtypes_row[0]] = subtypes_row[1:]

    all_subtypes = _SUBTYPES.get(target_type, [])
    subtypes_sample = [subtype for subtype in all_subtypes if "sun." not in subtype]  # filter Sun-specific types
    if len(subtypes_sample) > MAX_SUBTYPES_SAMPLE_SIZE:
        logger.warning("Sampling %r of %r subtypes...", MAX_SUBTYPES_SAMPLE_SIZE, len(subtypes_sample))
        subtypes_sample = subtypes_sample[:MAX_SUBTYPES_SAMPLE_SIZE]
    return subtypes_sample


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(IndentFormatter("%(indent)s%(message)s"))
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
    boa = BOA(username, password)
    for row in csv.reader(index, delimiter="\t"):
        project_id = row[0]
        version_id = row[1]
        target_type = row[2]
        try:
            logger.info("Preparing examples for %s.%s (target type: %s)", project_id, version_id, target_type)
            projects = boa.query_projects_with_type_usages(target_type, _get_subtypes(target_type))
            target_example_file = os.path.join(CHECKOUTS_PATH, target_type + ".yml")
            _prepare_example_projects(projects, target_example_file)
        except UserWarning as warning:
            logger.warning("%r", warning)
        except Exception as error:
            logger.exception("failed", exc_info=error)
