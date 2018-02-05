import os

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from tasks.implementations.collect_misuses import CollectMisusesTask
from tasks.implementations.collect_projects import CollectProjectsTask
from tasks.implementations.collect_versions import CollectVersionsTask
from tasks.task_runner import TaskRunner
from utils.data_entity_lists import DataEntityLists
from utils.dataset_util import get_white_list

DATASET_NAME = "FSE18-Extension"

MUBENCH_ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
MUBENCH_DATA_PATH = os.path.join(MUBENCH_ROOT_PATH, "data")
MUBENCH_DATASETS_FILE = os.path.join(MUBENCH_DATA_PATH, "datasets.yml")


class PrintIndexTask:
    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(project.id, version.version_id, misuse.misuse_id,
                                                  ':'.join(version.source_dirs),
                                                  misuse.location.file, misuse.location.method, misuse.apis[0]))


white_list = get_white_list(MUBENCH_DATASETS_FILE, DATASET_NAME)
initial_parameters = [DataEntityLists(white_list, [])]
TaskRunner([
    CollectProjectsTask(MUBENCH_DATA_PATH),
    CollectVersionsTask(False),
    CollectMisusesTask(),
    PrintIndexTask()
]).run(*initial_parameters)
