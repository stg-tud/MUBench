from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import ProjectTask, Response


class ProjectVersionTask(ProjectTask):
    def process_project(self, project: Project) -> Response:
        for version in project.versions:
            response = self.process_project_version(project, version)
            if response is Response.skip:
                return Response.skip

        return Response.ok

    def process_project_version(self, project: Project, version: ProjectVersion) -> Response:
        raise NotImplementedError


