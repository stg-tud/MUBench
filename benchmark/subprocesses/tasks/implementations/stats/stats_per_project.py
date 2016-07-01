# coding=utf-8
#
# Prints statistics about the API misuses per project.
#

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask


class perproject(ProjectVersionMisuseTask):
    def __init__(self):
        super().__init__()
        self.projects = {}

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        projectname = project.name
        project = self.projects.get(projectname, {"misuses": 0, "crashes": 0})
        project["misuses"] += 1
        if misuse.is_crash:
            project["crashes"] += 1
        self.projects[projectname] = project

    def end(self):
        print()
        print("  %40s %10s %15s" % ("Project", "Misuses", "Crashes"))
        for projectname in self.projects:
            project = self.projects[projectname]
            print("  %40s %10d %5d - % 6.1f%%" % (
                projectname, project["misuses"], project["crashes"], (project["crashes"] / project["misuses"] * 100)))
