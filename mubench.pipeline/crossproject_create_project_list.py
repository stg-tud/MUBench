import csv
import logging
import os
from datetime import datetime
from os.path import exists, join

from utils.io import open_yamls_if_exists, write_yaml
from utils.logging import IndentFormatter
from utils.shell import Shell

MUBENCH_ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
CHECKOUTS_PATH = os.path.join(MUBENCH_ROOT_PATH, "checkouts", "_examples")
INDEX_PATH = os.path.join(CHECKOUTS_PATH, "index.csv")

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

example_projects_by_API = {}
with open(INDEX_PATH) as index:
    for row in csv.reader(index, delimiter="\t"):
        target_type = row[6]
        try:
            if target_type not in example_projects_by_API:
                logger.info("Preparing examples for type: %s...", target_type)
                target_example_file = os.path.join(CHECKOUTS_PATH, target_type + ".yml")
                example_projects = {}
                with open_yamls_if_exists(target_example_file) as projects:
                    for project in projects:
                        hash = Shell.exec("cd \"{}\"; git rev-parse HEAD".format(join(MUBENCH_ROOT_PATH, project["path"])))
                        example_projects[project["url"]] = hash.strip()
                example_projects_by_API[target_type] = example_projects
        except Exception as error:
            logger.exception("failed", exc_info=error)

write_yaml(example_projects_by_API, join(CHECKOUTS_PATH, "example_projects_by_API.yml"))
