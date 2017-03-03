import logging
from typing import List

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from tasks.project_version_task import ProjectVersionTask


class ProjectVersionMisuseTask(ProjectVersionTask):
    def process_project_version(self, project: Project, version: ProjectVersion) -> List[str]:
        black_list = []

        for misuse in version.misuses:
            if self.__skip_misuse(project, version, misuse):
                logger = logging.getLogger("versions.misuses")
                logger.debug("Skipping %s", misuse)
            else:
                response = self.process_project_version_misuse(project, version, misuse)
                black_list.extend(response)

        return black_list

    def __skip_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        blacklisted = misuse.id in self.black_list
        whitelisted = misuse.id in self.white_list or version.id in self.white_list or project.id in self.white_list
        return blacklisted or (self.white_list and not whitelisted)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> List[str]:
        raise NotImplementedError
