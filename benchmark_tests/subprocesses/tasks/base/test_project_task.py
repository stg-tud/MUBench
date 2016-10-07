from nose.tools import assert_equals

from benchmark.subprocesses.tasks.base.project_task import ProjectTask


class TestProjectsTask:
    def test_white_list_static(self):
        expected = ["-test-"]
        uut = ProjectTask()

        ProjectTask.white_list = expected

        assert_equals(expected, uut.white_list)

    def test_black_list_static(self):
        expected = ["-test-"]
        uut = ProjectTask()

        ProjectTask.black_list = expected

        assert_equals(expected, uut.black_list)