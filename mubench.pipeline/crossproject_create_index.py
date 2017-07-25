from typing import List

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from task_runner import TaskRunner
from tasks.project_version_misuse_task import ProjectVersionMisuseTask
from utils.dataset_util import get_white_list


class Task(ProjectVersionMisuseTask):
    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> List[str]:
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(project.id, version.version_id, misuse.misuse_id, version.source_dir, misuse.location.file, misuse.location.method, misuse.apis[0]))
        return self.ok()

white_list = get_white_list("../data/datasets.yml", "icse16ex1")
runner = TaskRunner("../data/", white_list, [])
runner.add(Task())
runner.run()
