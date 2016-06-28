from tempfile import mkdtemp
from typing import List
from unittest.mock import MagicMock, call

from nose.tools import assert_equals

from benchmark.data.project import Project
from benchmark.subprocesses.tasking import TaskRunner
from benchmark.subprocesses.tasks.base.project_task import ProjectTask, Response
from benchmark.utils.io import remove_tree
from benchmark_tests.test_utils.data_util import create_project


# noinspection PyAttributeOutsideInit
class TestTaskRunner:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-datareader-test_')

        self.uut = TaskRunner("", white_list=[], black_list=[])

        self.test_projects = list()  # type: List[Project]
        self.uut._get_projects = lambda path: self.test_projects

        self.test_task = MagicMock()  # type: ProjectTask
        self.uut.add(self.test_task)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_processes_project(self):
        project = create_project("p1")
        self.test_projects.append(project)

        self.uut.run()

        self.test_task.process_project.assert_called_with(project)

    def test_starts_task(self):
        self.uut.run()

        self.test_task.start.assert_called_with()

    def test_ends_task(self):
        self.uut.run()

        self.test_task.end.assert_called_with()

    def test_skips_blacklisted_project(self):
        self.test_projects.append(create_project("p1"))
        self.uut.black_list.append("p1")

        self.uut.run()

        self.test_task.process_project.assert_not_called()

    def test_runs_only_whitelisted_project(self):
        p2 = create_project("p2")
        self.test_projects.extend([create_project("p1"), p2])
        self.uut.white_list.append("p2")

        self.uut.run()

        assert_equals([call(p2)], self.test_task.process_project.call_args_list)

    def test_adds_project_to_backlist_when_task_answers_skip(self):
        self.test_projects.append(create_project("p1"))
        self.test_task.process_project = MagicMock(return_value=Response.skip)

        self.uut.run()

        assert_equals(["p1"], self.uut.black_list)
