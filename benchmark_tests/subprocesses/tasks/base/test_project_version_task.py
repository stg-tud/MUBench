from typing import List
from typing import Tuple
from unittest.mock import MagicMock, call

from nose.tools import assert_equals

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark_tests.subprocesses.test_taskrunner import create_project


class TestProjectVersionTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version1 = create_version("v1")
        self.version2 = create_version("v2")
        self.project = create_project("p1", versions=[self.version1, self.version2])

        self.uut = ProjectVersionTask()
        self.uut.process_project_version = MagicMock()

    def test_process_version(self):
        self.uut.process_project(self.project)

        assert_equals([call(self.project, self.version1), call(self.project, self.version2)],
                      self.uut.process_project_version.call_args_list)


def create_version(path: str, misuses: List[Misuse] = None):
    version = ProjectVersion(path)
    version._MISUSES = [] if misuses is None else misuses
    version._YAML = {}
    return version


class ProjectVersionTaskTestImpl(ProjectVersionTask):
    def __init__(self):
        self.args = list()  # type: List[Tuple[Project, ProjectVersion]]

    def process_project_version(self, project: Project, version: ProjectVersion) -> Response:
        self.args.append((project, version))
        return Response.ok
