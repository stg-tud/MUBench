from enum import Enum
from typing import List, Set

from benchmark.data.project import Project


class Response(Enum):
    ok = 0
    skip = 1


class Requirement:
    def __init__(self, description: str, check = None):
        self.description = description
        if not check:
            check = self.check
        self.check = check

    def check(self):
        raise NotImplementedError


class ProjectTask:
    def __init__(self):
        self.__black_list = []
        self.__white_list = []

    @property
    def name(self):
        return type(self).__name__.lower()

    @property
    def black_list(self):
        return self.__black_list

    @black_list.setter
    def black_list(self, black_list: List[str]):
        self.__black_list = black_list

    @property
    def white_list(self):
        return self.__white_list

    @white_list.setter
    def white_list(self, white_list: List[str]):
        self.__white_list = white_list

    def get_requirements(self) -> Set[Requirement]:
        return []

    def start(self) -> None:
        pass

    def process_project(self, project: Project) -> Response:
        raise NotImplementedError

    def end(self) -> None:
        pass
