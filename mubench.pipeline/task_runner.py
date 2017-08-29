import logging
from datetime import datetime
from os import listdir
from os.path import exists, join
from typing import List

from data.project import Project
from tasks.project_task import ProjectTask


class TaskRunner:
    def __init__(self, data_path: str, white_list: List[str], black_list: List[str]):
        self.tasks = [] # type: List[ProjectTask]
        self.data_path = data_path
        self.white_list = white_list
        self.black_list = black_list

    def add(self, task: ProjectTask):
        self.tasks.append(task)

    def run(self) -> None:
        for task in self.tasks:
            logger = logging.getLogger()
            logger.info("Starting %s %s...", task.name, datetime.now().strftime("at %H:%M:%S"))
            task.black_list = self.black_list
            task.white_list = self.white_list
            task.start()
            for project in self._get_projects(self.data_path):
                logger = logging.getLogger("project")
                if self.__skip(project):
                    logger.debug("Skipping %s", project)
                else:
                    response = task.process_project(project)
                    if response:
                        if project.id in response:
                            logger.info("Cannot proceed on %s; skipping for subsequent tasks.", project)
                        self.black_list.extend(response)
            task.end()

    @staticmethod
    def _get_projects(data_path: str) -> List[Project]:
        project_ids = []
        if exists(data_path):
            project_ids.extend(sorted(listdir(data_path)))

        return [Project(data_path, project_id) for project_id in project_ids if
                Project.is_project(join(data_path, project_id))]

    def __skip(self, project: Project) -> bool:
        blacklisted = project.id in self.black_list
        whitelisted = any(item.startswith(project.id) for item in self.white_list)
        return blacklisted or (self.white_list and not whitelisted)
