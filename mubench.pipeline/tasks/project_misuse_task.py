import logging
from typing import List

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from tasks.project_task import ProjectTask


class ProjectMisuseTask(ProjectTask):
    def process_project(self, project: Project) -> List[str]:
        black_list = []

        misuses = set()
        for version in project.versions:
            for misuse in version.misuses:
                if misuse not in misuses:
                    if self.__skip(project, version, misuse):
                        logger = logging.getLogger("misuses")
                        logger.debug("Skipping %s", misuse)
                    else:
                        response = self.process_project_misuse(project, misuse)
                        black_list.extend(response)

                misuses.add(misuse)

        return black_list

    def __skip(self, project: Project, version: ProjectVersion, misuse: Misuse):
        blacklisted = misuse.id in self.black_list
        whitelisted = misuse.id in self.white_list or version.id in self.white_list or project.id in self.white_list
        return blacklisted or (self.white_list and not whitelisted)

    def process_project_misuse(self, project: Project, misuse: Misuse) -> List[str]:
        raise NotImplementedError
