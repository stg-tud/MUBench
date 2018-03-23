# coding=utf-8
import logging
from typing import Optional, List, Dict

import yaml

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion


class StatCalculatorTask:
    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
        raise NotImplementedError

    def end(self):
        raise NotImplementedError


def get_available_calculators() -> List[type]:
    return StatCalculatorTask.__subclasses__()


def get_available_calculator_names() -> List[str]:
    return [calculator.__name__ for calculator in get_available_calculators()]


def get_calculator(name: str) -> Optional[StatCalculatorTask]:
    for calculator in get_available_calculators():
        if calculator.__name__.lower() == name.lower():
            return calculator()


class general(StatCalculatorTask):
    def __init__(self):
        super().__init__()
        self.number_of_misuses = 0
        self.number_of_misuses_with_corresponding_correct_usages = 0
        self.number_of_multitype_misuses = 0
        self.number_of_internal_API_misuses = 0
        self.number_of_crashes = 0
        self.projects = set()
        self.versions = set()
        self.sources = set()
        self.apis = set()

        self.logger = logging.getLogger('stats.general')

    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
        self.sources.add(misuse.source)
        if not project.id.startswith("synthetic_"):
            self.projects.add(project.id)
            self.versions.add(version.id)

        self.number_of_misuses += 1

        if len(misuse.apis) > 1:
            self.number_of_multitype_misuses += 1

        if misuse.is_apis_are_internal:
            self.number_of_internal_API_misuses += 1

        if misuse.is_crash:
            self.number_of_crashes += 1

        if misuse.patterns:
            self.number_of_misuses_with_corresponding_correct_usages += 1

        self.apis.add(tuple(sorted(misuse.apis)))

    def end(self):
        self.log("Property", "Value")
        self.log("-" * 33, "")
        self.log("Sources", len(self.sources))
        self.log("Projects", len(self.projects))
        self.log("Versions", len(self.versions))
        self.log("Misuses", self.number_of_misuses)
        self.log("    Multi-Type", self.number_of_multitype_misuses, self.number_of_misuses)
        self.log("    Internal-API", self.number_of_internal_API_misuses, self.number_of_misuses)
        self.log("    Crash", self.number_of_crashes, self.number_of_misuses)
        self.log("    Correct Usage", self.number_of_misuses_with_corresponding_correct_usages, self.number_of_misuses)
        self.log("Misused APIs", len(self.apis))

    def log(self, key, value, total=None):
        percentage = "({: >5.1f}%)".format(value / total * 100) if total else ""
        self.logger.info("{: <18} {: >5} {}".format(key, value, percentage))


class violation(StatCalculatorTask):
    def __init__(self):
        super().__init__()
        self.statistics = {}
        self.total = " total"
        self.logger = logging.getLogger('stats.characteristic')

    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
        chars = misuse.characteristics
        for char in chars:
            seg = char.split('/')
            statname = seg[0] + " " + seg[1]
            stat = self.statistics.get(statname, {self.total: {"misuses": 0, "crashes": 0}})
            stat[self.total]["misuses"] += 1
            if misuse.is_crash:
                stat[self.total]["crashes"] += 1

            if len(seg) > 2:
                segstat = stat.get(seg[2], {"misuses": 0, "crashes": 0})
                segstat["misuses"] += 1
                if misuse.is_crash:
                    segstat["crashes"] += 1
                stat[seg[2]] = segstat

            self.statistics[statname] = stat

    def end(self):
        self.logger.info("{: <30} {: <7} {}".format("Violation", "Misuses", "Crashes"))
        self.logger.info("{}".format("-" * 52))

        for statistic in sorted(self.statistics.items(), key=lambda s: s[0]):
            statistic_name = statistic[0]
            statistic_values = statistic[1]
            for segstat in sorted(statistic_values):
                if segstat == self.total:
                    violation = statistic_name
                else:
                    violation = "    {}".format(segstat)

                self.logger.info("{: <30} {: >7} {: >4} ({: >5.1f}%)".format(
                    violation,
                    statistic_values[segstat]["misuses"], statistic_values[segstat]["crashes"],
                    statistic_values[segstat]["crashes"] / statistic_values[segstat]["misuses"] * 100))


class project(StatCalculatorTask):
    def __init__(self):
        super().__init__()
        self.projects = {}

        self.logger = logging.getLogger('stats.project')

    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
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


class source(StatCalculatorTask):
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

    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
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


class misusesbytype(StatCalculatorTask):
    def __init__(self):
        super().__init__()
        self.index = {}  # type: Dict[str, List[Misuse]]

    def start(self):
        self.index.clear()

    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
        for characteristic in misuse.characteristics:
            if characteristic not in self.index:
                self.index[characteristic] = []

            self.index[characteristic].append(misuse)

    def end(self):
        logger = logging.getLogger('stats.misusesbytype')
        logger.info("%35s %s", "Violation Type", "Misuse")
        for characteristic in sorted(self.index):
            logger.info("%35s ----------------------------", characteristic)
            for misuse in self.index[characteristic]:
                logger.info("%35s %s", "", misuse.id)
