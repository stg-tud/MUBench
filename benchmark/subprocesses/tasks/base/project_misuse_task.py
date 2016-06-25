from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.subprocesses.tasks.base.project_task import ProjectTask, Response


class ProjectMisuseTask(ProjectTask):
    def process_project(self, project: Project) -> Response:
        misuses = set()
        for version in project.versions:
            for misuse in version.misuses:
                misuses.add(misuse)

        for misuse in misuses:
            response = self.process_project_misuse(project, misuse)
            if response is Response.skip:
                return Response.skip

        return Response.ok

    def process_project_misuse(self, project: Project, misuse: Misuse) -> Response:
        raise NotImplementedError
