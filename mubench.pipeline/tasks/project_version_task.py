import logging
from typing import List

from data.project import Project
from data.project_version import ProjectVersion
from tasks.project_task import ProjectTask


class ProjectVersionTask(ProjectTask):
    def process_project(self, project: Project) -> List[str]:
        logger = logging.getLogger("versions")
        black_list = []
        for version in project.versions:
            if self.__skip(version):
                logger.debug("Skipping %s", version)
            else:
                response = self.process_project_version(project, version)
                if response:
                    logger.info("Cannot proceed on %s; skipping for subsequent tasks.", version)
                    black_list.extend(response)

        return black_list

    def __skip(self, version: ProjectVersion):
        blacklisted = version.id in self.black_list
        has_whitelisted_misuse = [misuse for misuse in version.misuses if misuse.id in self.white_list]
        whitelisted = version.id in self.white_list or version.project_id in self.white_list or has_whitelisted_misuse
        return blacklisted or (self.white_list and not whitelisted)

    def process_project_version(self, project: Project, version: ProjectVersion) -> List[str]:
        raise NotImplementedError
