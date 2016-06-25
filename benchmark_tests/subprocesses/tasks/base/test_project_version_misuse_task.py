from typing import List
from typing import Tuple

from nose.tools import assert_equals

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark_tests.test_utils.data_util import create_misuse, create_version, create_project


class TestProjectVersionMisuseTask:
    def test_process_misuse(self):
        uut = ProjectVersionMisuseTaskTestImpl()

        test_misuses = [create_misuse("m1"), create_misuse("m2"), create_misuse("m3")]
        test_versions = [create_version("v1", test_misuses[0:2]), create_version("v2", [test_misuses[2]])]
        test_project = create_project("p1", test_versions)

        uut.process_project(test_project)

        assert_equals(3, len(uut.args))
        assert_equals((test_project, test_versions[0], test_misuses[0]), uut.args[0])
        assert_equals((test_project, test_versions[0], test_misuses[1]), uut.args[1])
        assert_equals((test_project, test_versions[1], test_misuses[2]), uut.args[2])


class ProjectVersionMisuseTaskTestImpl(ProjectVersionMisuseTask):
    def __init__(self):
        self.start_was_called_correctly = False
        self.end_was_called_correctly = False
        self.args = list()  # type: List[Tuple[Project, ProjectVersion, Misuse]

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        self.args.append((project, version, misuse))
        return Response.ok
