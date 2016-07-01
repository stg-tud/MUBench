# coding=utf-8
#
# Prints statistics about the API misuses in the entire dataset.
#
import logging

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask


class general(ProjectVersionMisuseTask):
    def __init__(self):
        super().__init__()
        self.number_of_misuses = 0
        self.number_of_crashes = 0
        self.projects = set()
        self.sources = set()

        self.logger = logging.getLogger('stats.general')

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        self.number_of_misuses += 1
        if misuse.is_crash:
            self.number_of_crashes += 1

        self.sources.add(misuse.source)

        if project.name is not None:
            self.projects.add(project.name)
        else:
            # TODO: is this correct?
            self.projects.add("survey")

    def end(self):
        self.logger.info("MUBench contains:")
        self.logger.info("- %d misuses" % self.number_of_misuses)
        self.logger.info(
            "- %d crashes (%.1f%%)" % (self.number_of_crashes, (self.number_of_crashes / self.number_of_misuses * 100)))
        self.logger.info("- %d sources" % len(self.sources))
        self.logger.info("- %d projects" % len(self.projects))
