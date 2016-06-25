from enum import Enum

from benchmark.data.project import Project


class Response(Enum):
    ok = 0
    skip = 1


class ProjectTask:
    def start(self) -> None:
        pass

    def process_project(self, project: Project) -> Response:
        raise NotImplementedError

    def end(self) -> None:
        pass
