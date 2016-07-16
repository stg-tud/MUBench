from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask


class ProjectVersionMisuseTask(ProjectVersionTask):
    def process_project_version(self, project: Project, version: ProjectVersion):
        for misuse in version.misuses:
            self.new_version(project, version)
            self.process_project_version_misuse(project, version, misuse)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        raise NotImplementedError

    def new_version(self, project: Project, version: ProjectVersion):
        pass
