import logging
from typing import List

from benchmark.data.project import Project
from benchmark.subprocesses.tasks.base.project_task import ProjectTask, Response


class TaskRunner:
    def __init__(self, data_path: str, white_list: List[str], black_list: List[str]):
        self.tasks = []
        self.data_path = data_path
        self.white_list = white_list
        self.black_list = black_list

    def add(self, task: ProjectTask):
        self.tasks.append(task)

    def run(self) -> None:
        for task in self.tasks:
            logger = logging.getLogger()
            logger.info("Starting %s...", type(task).__name__.lower())
            task.start()
            for project in self._get_projects(self.data_path):
                logger = logging.getLogger("project")
                if self.__skip(project):
                    logger.debug("Skipping '%s'", project.id)
                else:
                    response = task.process_project(project)
                    if response == Response.skip:
                        logger.info("Cannot proceed on project '%s'; skipping for subsequent tasks.")
                        self.black_list.append(project.id)
            task.end()

    @staticmethod
    def _get_projects(data_path: str) -> List[Project]:
        return Project.get_projects(data_path)

    def __skip(self, project: Project) -> bool:
        return project.id in self.black_list or (self.white_list and project.id not in self.white_list)
