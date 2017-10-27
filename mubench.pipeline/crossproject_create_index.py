from typing import List

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from tasks.implementations.collect_misuses import CollectMisusesTask
from tasks.implementations.collect_projects import CollectProjectsTask
from tasks.implementations.collect_versions import CollectVersionsTask
from tasks.task_runner import TaskRunner
from utils.data_entity_lists import DataEntityLists
from utils.data_filter import DataFilter
from utils.dataset_util import get_white_list


class Task:
    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> List[str]:
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(project.id, version.version_id, misuse.misuse_id, version.source_dir, misuse.location.file, misuse.location.method, misuse.apis[0]))
        return [self]


white_list = get_white_list("../data/datasets.yml", "icse16ex1")
data_filter = DataFilter(white_list, [])
data_entity_lists = DataEntityLists(white_list, [])
runner = TaskRunner(
    [CollectProjectsTask("../data/", data_entity_lists), CollectVersionsTask(data_filter),
     CollectMisusesTask(data_filter),
     Task()])
runner.run()
