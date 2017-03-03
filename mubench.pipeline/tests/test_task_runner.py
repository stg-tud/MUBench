from os.path import join
from tempfile import mkdtemp
from unittest.mock import MagicMock, call

from nose.tools import assert_equals, assert_raises

from tasks.project_task import ProjectTask, Requirement
from task_runner import TaskRunner
from utils.io import remove_tree, create_file
from tests.test_utils.data_util import create_project


# noinspection PyAttributeOutsideInit
class TestTaskRunner:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-datareader-test_')
        self.test_task = MagicMock()  # type: ProjectTask

        self.uut = TaskRunner(self.temp_dir, white_list=[], black_list=[])
        self.uut.add(self.test_task)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_processes_project(self):
        project = create_project("p1")
        self.uut._get_projects = MagicMock(return_value=[project])

        self.uut.run()

        self.test_task.process_project.assert_called_with(project)

    def test_checks_requirements(self):
        requirement = Requirement("test requirement")
        requirement.check = MagicMock()
        self.test_task.get_requirements = MagicMock(return_value=[requirement])

        self.uut.run()

        requirement.check.assert_called_with()

    def test_stops_on_unsatisfied_requirement(self):
        requirement = Requirement("test requirement")
        requirement.check = MagicMock(side_effect=ValueError("not satisfied"))
        self.test_task.get_requirements = MagicMock(return_value=[requirement])

        with assert_raises(SystemExit):
            self.uut.run()

        # assert that exit comes before task is started
        self.test_task.start.assert_not_called()

    def test_starts_task(self):
        self.uut.run()

        self.test_task.start.assert_called_with()

    def test_ends_task(self):
        self.uut.run()

        self.test_task.end.assert_called_with()

    def test_finds_all_projects(self):
        p1 = create_project("p1", base_path=self.temp_dir)
        create_file(p1._project_file)
        p2 = create_project("p2", base_path=self.temp_dir)
        create_file(p2._project_file)

        self.uut.run()

        assert_equals([call(p1), call(p2)], self.test_task.process_project.call_args_list)

    def test_ignores_non_project_directories(self):
        create_file(join(self.temp_dir, "p1", "iamnotaproject.yml"))

        self.uut.run()

        self.test_task.process_project.assert_not_called()

    def test_skips_blacklisted_project(self):
        self.uut._get_projects = MagicMock(return_value=[create_project("p1")])
        self.uut.black_list.append("p1")

        self.uut.run()

        self.test_task.process_project.assert_not_called()

    def test_runs_only_whitelisted_project(self):
        p2 = create_project("p2")
        self.uut._get_projects = MagicMock(return_value=[create_project("p1"), p2])
        self.uut.white_list.append("p2")

        self.uut.run()

        assert_equals([call(p2)], self.test_task.process_project.call_args_list)

    def test_runs_whitelisted_project_if_version_only_whitelist(self):
        project = create_project("p")
        self.uut._get_projects = MagicMock(return_value=[project])
        self.uut.white_list.append("p.42")

        self.uut.run()

        self.test_task.process_project.assert_called_with(project)

    def test_adds_project_to_backlist_when_task_answers_skip(self):
        self.uut._get_projects = MagicMock(return_value=[(create_project("p1"))])
        self.test_task.process_project = MagicMock(return_value=["p1"])

        self.uut.run()

        assert_equals(["p1"], self.uut.black_list)
