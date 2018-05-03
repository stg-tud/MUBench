import csv
from typing import List

from data.misuse import Misuse
from data.project_version import ProjectVersion


class CrossProjectMisuseApi:
    def __init__(self, row):
        self.project_id = row[0]
        self.version_id = row[1]
        self.misuse_id = row[2]
        self.target_types = sorted(row[6:])


class CrossProjectMisuseApis:
    def __init__(self, apis: List[CrossProjectMisuseApi]):
        self.__apis = apis

    def get(self):
        return list(self.__apis)


class CrossProjectReadIndexTask:
    def __init__(self, index_file: str):
        self.index = index_file

    def run(self):
        apis = []

        with open(self.index) as index_file:
            for row in csv.reader(index_file, delimiter="\t"):
                # skip blank lines, e.g., on trailing newline
                if row:
                    apis.append(CrossProjectMisuseApi(row))

        return CrossProjectMisuseApis(apis)


class CrossProjectReadIndexPerMisuseTask:
    def __init__(self, index_file: str):
        self.index = index_file

    def run(self, misuse: Misuse):
        apis = []

        with open(self.index) as index_file:
            for row in csv.reader(index_file, delimiter="\t"):
                # skip blank lines, e.g., on trailing newline
                if row and misuse.id == ".".join(row[:3]).lower():
                    apis.append(CrossProjectMisuseApi(row))

        return CrossProjectMisuseApis(apis)


class CrossProjectReadIndexPerVersionTask:
    def __init__(self, index_file: str):
        self.index = index_file

    def run(self, version: ProjectVersion):
        apis = []

        with open(self.index) as index_file:
            for row in csv.reader(index_file, delimiter="\t"):
                # skip blank lines, e.g., on trailing newline
                if row and version.id == ".".join(row[:2]).lower():
                    apis.append(CrossProjectMisuseApi(row))

        return CrossProjectMisuseApis(apis)


class CrossProjectSkipReadIndexTask:
    def run(self):
        return CrossProjectMisuseApis([])
