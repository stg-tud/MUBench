from tempfile import mkdtemp
from typing import List

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

        self.test_task = ProjectTaskTestImpl()

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_process_project(self):
        self.test_projects.append(create_project("p1"))

        self.uut.add(self.test_task)
        self.uut.run()

        assert_equals(self.test_projects, self.test_task.projects)

    def test_start_called_correctly(self):
        self.test_projects.append(create_project("p1"))

        self.uut.add(self.test_task)
        self.uut.run()

        assert self.test_task.start_was_called_correctly

    def test_end_called_correctly(self):
        self.test_projects.append(create_project("p1"))

        self.uut.add(self.test_task)
        self.uut.run()

        assert self.test_task.end_was_called_correctly

    def test_skip_project(self):
        self.test_projects.append(create_project("p1"))

        class SkipProjectTask(ProjectTask):
            def process_project(self, project: Project) -> Response:
                return Response.skip

        self.uut.add(SkipProjectTask())
        self.uut.add(self.test_task)
        self.uut.run()

        assert_equals(0, len(self.test_task.projects))

    def test_black_list(self):
        self.uut.black_list.append("p1")
        self.test_projects.append(create_project("p1"))

        self.uut.add(self.test_task)
        self.uut.run()

        assert_equals([], self.test_task.projects)

    def test_white_list(self):
        self.uut.white_list.append("p2")
        self.test_projects.append(create_project("p1"))
        p2 = create_project("p2")
        self.test_projects.append(p2)

        self.uut.add(self.test_task)
        self.uut.run()

        assert_equals([p2], self.test_task.projects)


class ProjectTaskTestImpl(ProjectTask):
    def __init__(self):
        self.start_was_called_correctly = False
        self.end_was_called_correctly = False
        self.projects = list()  # type: List[Project]

    def start(self) -> None:
        if not self.projects:
            self.start_was_called_correctly = True

    def process_project(self, project: Project) -> Response:
        self.projects.append(project)
        return Response.ok

    def end(self) -> None:
        if self.projects:
            self.end_was_called_correctly = True
