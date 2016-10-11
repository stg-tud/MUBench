from typing import List

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.subprocesses.tasks.base.project_task import ProjectTask


class ProjectMisuseTask(ProjectTask):
    def process_project(self, project: Project) -> List[str]:
        black_list = []

        misuses = set()
        for version in project.versions:
            for misuse in version.misuses:
                misuses.add(misuse)

        for misuse in misuses:
            response = self.process_project_misuse(project, misuse)
            black_list.extend(response)

        return black_list

    def process_project_misuse(self, project: Project, misuse: Misuse) -> List[str]:
        raise NotImplementedError
