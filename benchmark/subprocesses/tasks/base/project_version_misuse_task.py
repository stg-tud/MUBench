from typing import List

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask


class ProjectVersionMisuseTask(ProjectVersionTask):
    def process_project_version(self, project: Project, version: ProjectVersion) -> List[str]:
        black_list = []
        for misuse in version.misuses:
            response = self.process_project_version_misuse(project, version, misuse)
            black_list.extend(response)
        return black_list

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> List[str]:
        raise NotImplementedError
