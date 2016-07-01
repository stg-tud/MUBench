# coding=utf-8
#
# Prints statistics about the API misuses per characteristic.
#
import logging

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask


class percharacteristic(ProjectVersionMisuseTask):
    def __init__(self):
        super().__init__()
        self.statistics = {}

        self.logger = logging.getLogger('stats.percharacteristic')

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        chars = misuse.characteristics
        for char in chars:
            seg = char.split('/')
            stat = self.statistics.get(seg[0], {"total": {"misuses": 0, "crashes": 0}})
            stat["total"]["misuses"] += 1
            if misuse.is_crash:
                stat["total"]["crashes"] += 1

            if len(seg) > 1:
                segstat = stat.get(seg[1], {"misuses": 0, "crashes": 0})
                segstat["misuses"] += 1
                if misuse.is_crash:
                    segstat["crashes"] += 1
                stat[seg[1]] = segstat

            self.statistics[seg[0]] = stat

    def end(self):
        self.logger.info("%25s %25s %7s %14s" % ("Characteristic", "SubCharacteristic", "Misuses", "Crashes"))
        for statname in self.statistics:
            stat = self.statistics[statname]
            for segstat in stat:
                self.logger.info("%25s %25s %7d %7d% 6.1f%%" % (
                    statname, segstat, stat[segstat]["misuses"], stat[segstat]["crashes"],
                    (stat[segstat]["crashes"] / stat[segstat]["misuses"] * 100)))
