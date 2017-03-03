from unittest.mock import MagicMock, call

from nose.tools import assert_equals
from nose.tools import assert_in

from tasks.project_misuse_task import ProjectMisuseTask
from tests.test_utils.data_util import create_misuse, create_version, create_project


class TestProjectVersionMisuseTask:
    def test_process_misuse(self):
        uut = ProjectMisuseTask()
        uut.process_project_misuse = MagicMock()

        project = create_project("p1")
        m1 = create_misuse("m1")
        m2 = create_misuse("m2")
        m3 = create_misuse("m3")
        create_version("v1", misuses=[m1, m2], project=project)
        create_version("v2", misuses=[m3], project=project)

        uut.process_project(project)

        actual_call = uut.process_project_misuse.call_args_list
        assert_equals(3, len(actual_call))
        assert_in(call(project, m1), actual_call)
        assert_in(call(project, m2), actual_call)
        assert_in(call(project, m3), actual_call)

    def test_white_list_misuse(self):
        uut = ProjectMisuseTask()
        uut.process_project_misuse = MagicMock()

        project = create_project("-p-")
        misuse1 = create_misuse("-m1-", project=project)
        misuse2 = create_misuse("-m2-", project=project)
        create_version("-v-", misuses=[misuse1, misuse2], project=project)

        uut.white_list = [misuse1.id]

        uut.process_project(project)

        assert_equals([call(project, misuse1)], uut.process_project_misuse.call_args_list)

    def test_white_list_project(self):
        uut = ProjectMisuseTask()
        uut.process_project_misuse = MagicMock()

        project1 = create_project("-p1-")
        project2 = create_project("-p2-")
        misuse1 = create_misuse("-m1-", project=project1)
        misuse2 = create_misuse("-m2-", project=project2)
        create_version("-v1-", misuses=[misuse1], project=project1)
        create_version("-v2-", misuses=[misuse2], project=project2)

        uut.white_list = [project1.id]

        uut.process_project(project1)
        uut.process_project(project2)

        assert_equals([call(project1, misuse1)], uut.process_project_misuse.call_args_list)

    def test_white_list_version(self):
        uut = ProjectMisuseTask()
        uut.process_project_misuse = MagicMock()

        project = create_project("-p-")
        misuse1 = create_misuse("-m1-", project=project)
        misuse2 = create_misuse("-m2-", project=project)
        version1 = create_version("-v1-", misuses=[misuse1], project=project)
        create_version("-v2-", misuses=[misuse2], project=project)

        uut.white_list = [version1.id]

        uut.process_project(project)

        assert_equals([call(project, misuse1)], uut.process_project_misuse.call_args_list)