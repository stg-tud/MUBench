from typing import List
from typing import Tuple

from nose.tools import assert_equals

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark_tests.subprocesses.test_taskrunner import create_project


class TestProjectVersionTask:
    def test_process_version(self):
        uut = ProjectVersionTaskTestImpl()
        test_versions = [create_version("v1"), create_version("v2")]
        test_project = create_project("p1", test_versions)

        uut.process_project(test_project)

        assert_equals(2, len(uut.args))
        assert_equals((test_project, test_versions[0]), uut.args[0])
        assert_equals((test_project, test_versions[1]), uut.args[1])


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
