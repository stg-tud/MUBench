# coding=utf-8
#
# Prints statistics about the API misuses per source.
#
import logging

import yaml

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask


class persource(ProjectVersionMisuseTask):
    def __init__(self):
        super().__init__()
        self.sources = {}

        self.logger = logging.getLogger('stats.persource')

    def start(self):
        filename = "sources.yml"
        with open(filename) as file:
            sources = yaml.load(file)
            for source in sources:
                sources[source]["misuses"] = 0
                sources[source]["crashes"] = 0

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        sourcename = misuse.source
        source = self.sources[sourcename]
        source["misuses"] += 1
        if misuse.is_crash:
            source["crashes"] += 1
        self.sources[sourcename] = source

    def end(self):
        self.logger.info("%20s %7s %9s %15s   %15s" % ("Source", "Size", "Reviewed", "Misuses", "Crashes"))
        for sourcename in self.sources:
            source = self.sources[sourcename]
            self.logger.info("%20s %7d %9d %5d - % 6.1f%%   %5d - % 6.1f%%" % (
                sourcename, source["size"], source["reviewed"], source["misuses"],
                (source["misuses"] / source["reviewed"] * 100), source["crashes"],
                (source["crashes"] / source["misuses"] * 100)))
