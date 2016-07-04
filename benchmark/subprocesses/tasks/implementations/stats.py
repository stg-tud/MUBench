# coding=utf-8
import logging
import yaml
from typing import Optional, List

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask


class StatCalculator(ProjectVersionMisuseTask):
    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        raise NotImplementedError

    def end(self):
        raise NotImplementedError


def get_available_calculators() -> List[type]:
    return StatCalculator.__subclasses__()


def get_available_calculator_names() -> List[str]:
    return [calculator.__name__ for calculator in get_available_calculators()]


def get_calculator(name: str) -> Optional[StatCalculator]:
    for calculator in get_available_calculators():
        if calculator.__name__.lower() == name.lower():
            return calculator()


class general(StatCalculator):
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


class challenge(StatCalculator):
    def __init__(self):
        super().__init__()
        self.statistics = {}

        self.logger = logging.getLogger('stats.challenge')

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        # TODO: does this still exist?
        if "challenges" in misuse._yaml:
            challs = misuse.challenges
            for chall in challs:
                stat = self.statistics.get(chall, 0)
                stat += 1
                self.statistics[chall] = stat

    def end(self):
        self.logger.info("%25s %7s" % ("Challenge", "Misuses"))
        for statname in self.statistics:
            self.logger.info("%25s %7d" % (statname, self.statistics[statname]))


class characteristic(StatCalculator):
    def __init__(self):
        super().__init__()
        self.statistics = {}

        self.logger = logging.getLogger('stats.characteristic')

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


class project(StatCalculator):
    def __init__(self):
        super().__init__()
        self.projects = {}

        self.logger = logging.getLogger('stats.project')

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        projectname = project.name
        project = self.projects.get(projectname, {"misuses": 0, "crashes": 0})
        project["misuses"] += 1
        if misuse.is_crash:
            project["crashes"] += 1
        self.projects[projectname] = project

    def end(self):
        self.logger.info("  %40s %10s %15s" % ("Project", "Misuses", "Crashes"))
        for projectname in self.projects:
            project = self.projects[projectname]
            self.logger.info("  %40s %10d %5d - % 6.1f%%" % (
                projectname, project["misuses"], project["crashes"], (project["crashes"] / project["misuses"] * 100)))


class source(StatCalculator):
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
        self.sources = sources

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
