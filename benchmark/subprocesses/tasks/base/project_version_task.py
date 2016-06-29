import logging

from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import ProjectTask, Response


class ProjectVersionTask(ProjectTask):
    def process_project(self, project: Project) -> Response:
        logger = logging.getLogger("versions")
        for version in project.versions:
            if self.__skip(version):
                logger.debug("Skipping %s", version)
            else:
                response = self.process_project_version(project, version)
                if response is Response.skip:
                    logger.info("Cannot proceed on %s; skipping for subsequent tasks.", version)
                    self.black_list.append(version.id)

        return Response.ok

    def __skip(self, version: ProjectVersion):
        blacklisted = version.id in self.black_list
        whitelisted = version.id in self.white_list or version.project_id in self.white_list
        return blacklisted or (self.white_list and not whitelisted)

    def process_project_version(self, project: Project, version: ProjectVersion) -> Response:
        raise NotImplementedError
