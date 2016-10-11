from unittest.mock import MagicMock, call

from nose.tools import assert_equals

from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark_tests.test_utils.data_util import create_misuse, create_version, create_project


class TestProjectVersionMisuseTask:
    def test_process_misuse(self):
        uut = ProjectVersionMisuseTask()
        uut.process_project_version_misuse = MagicMock()

        project = create_project("p1")
        m1 = create_misuse("m1")
        m2 = create_misuse("m2")
        m3 = create_misuse("m3")
        v1 = create_version("v1", misuses=[m1, m2], project=project)
        v2 = create_version("v2", misuses=[m3], project=project)

        uut.process_project(project)

        assert_equals([call(project, v1, m1), call(project, v1, m2), call(project, v2, m3)],
                      uut.process_project_version_misuse.call_args_list)
