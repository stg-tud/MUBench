# coding=utf-8
#
# Prints statistics about the API misuses per characteristic.
#

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask


class perchallenge(ProjectVersionMisuseTask):
    def __init__(self):
        super().__init__()
        self.statistics = {}

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        # TODO: does this still exist?
        if "challenges" in misuse:
            challs = misuse.challenges
            for chall in challs:
                stat = self.statistics.get(chall, 0)
                stat += 1
                self.statistics[chall] = stat

    def end(self):
        print()
        print("%25s %7s" % ("Challenge", "Misuses"))
        for statname in self.statistics:
            print("%25s %7d" % (statname, self.statistics[statname]))
