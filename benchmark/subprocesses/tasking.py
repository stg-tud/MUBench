import logging
from typing import List

from benchmark.data.project import Project
from benchmark.subprocesses.tasks.base.project_task import ProjectTask, Response


class TaskRunner:
    def __init__(self, data_path: str, white_list: List[str], black_list: List[str]):
        self._logger = logging.getLogger()
        self.tasks = []
        self.data_path = data_path
        self.white_list = white_list
        self.black_list = black_list

    def add(self, task: ProjectTask):
        self.tasks.append(task)

    def start(self) -> None:
        for task in self.tasks:
            try:
                self._logger.debug("Enter on '%s'", type(task).__name__)
                task.start()
            except Exception:
                self._logger.error("Error on enter", exc_info=True)
                raise

    def end(self) -> None:
        for task in self.tasks:
            try:
                self._logger.debug("Exit on '%s'", type(task).__name__)
                task.end()
            except Exception:
                self._logger.debug("Error on exit", exc_info=True)
                raise

    def process_project(self, project: Project) -> None:
        for task in self.tasks:
            if self.__skip(project.id):
                return

            response = task.process_project(project)
            if response is Response.skip:
                self.black_list.append(project.id)

    def run(self) -> None:
        projects = self._get_projects(self.data_path)
        self.start()
        for project in projects:
            self.process_project(project)
        self.end()

    @staticmethod
    def _get_projects(data_path: str) -> List[Project]:
        return Project.get_projects(data_path)

    def __skip(self, project_id: str) -> bool:
        return project_id in self.black_list or (self.white_list and project_id not in self.white_list)
