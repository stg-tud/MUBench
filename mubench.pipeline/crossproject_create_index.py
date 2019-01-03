import os

import sys

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from tasks.implementations.collect_misuses import CollectMisusesTask
from tasks.implementations.collect_projects import CollectProjectsTask
from tasks.implementations.collect_versions import CollectVersionsTask
from tasks.task_runner import TaskRunner
from utils.data_entity_lists import DataEntityLists
from utils.dataset_util import get_white_list


__MUBENCH_ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
__MUBENCH_DATA_PATH = os.path.join(__MUBENCH_ROOT_PATH, "data")
__MUBENCH_DATASETS_FILE = os.path.join(__MUBENCH_DATA_PATH, "datasets.yml")
_INDEX_PATH = os.path.join(__MUBENCH_ROOT_PATH, "checkouts-xp", "index.csv")


class PrintIndexTask:
    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(project.id, version.version_id, misuse.misuse_id,
                                                  ':'.join(version.source_dirs),
                                                  misuse.location.file, misuse.location.method,
                                                  "\t".join(misuse.apis)), file=open(_INDEX_PATH, "a"))


datasets = sys.argv[1:]

white_list = []
for dataset in datasets:
    white_list.extend(get_white_list(__MUBENCH_DATASETS_FILE, dataset.lower()))
initial_parameters = [DataEntityLists(white_list, [])]

runner = TaskRunner(
    [CollectProjectsTask(__MUBENCH_DATA_PATH), CollectVersionsTask(False), CollectMisusesTask(), PrintIndexTask()])

if os.path.exists(_INDEX_PATH):
    os.remove(_INDEX_PATH)

runner.run(*initial_parameters)
