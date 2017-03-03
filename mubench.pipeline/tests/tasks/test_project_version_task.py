from unittest.mock import MagicMock, call

from nose.tools import assert_equals

from tasks.project_version_task import ProjectVersionTask
from tests.test_utils.data_util import create_version, create_misuse, create_project


class TestProjectVersionTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.project = create_project("p1")
        self.version1 = create_version("v1", project=self.project)
        self.version2 = create_version("v2", project=self.project)

        self.uut = ProjectVersionTask()
        self.uut.black_list = []
        self.uut.white_list = []
        self.uut.process_project_version = MagicMock()

    def test_process_version(self):
        self.uut.process_project(self.project)

        assert_equals([call(self.project, self.version1), call(self.project, self.version2)],
                      self.uut.process_project_version.call_args_list)

    def test_adds_version_to_blacklist_when_task_returns_skip(self):
        self.uut.process_project_version = MagicMock(side_effect=iter([[self.version1.id], [self.version2.id]]))

        response = self.uut.process_project(self.project)

        assert_equals([self.version1.id, self.version2.id], response)

    def test_skips_version_on_blacklist(self):
        self.uut.black_list.append(self.version1.id)

        self.uut.process_project(self.project)

        assert_equals([call(self.project, self.version2)], self.uut.process_project_version.call_args_list)

    def test_skips_versions_not_on_whitelist(self):
        self.uut.white_list.append(self.version1.id)

        self.uut.process_project(self.project)

        assert_equals([call(self.project, self.version1)], self.uut.process_project_version.call_args_list)

    def test_processes_version_if_project_on_whitelist(self):
        self.uut.white_list.append(self.project.id)

        self.uut.process_project(self.project)

        assert_equals(2, len(self.uut.process_project_version.call_args_list))

    def test_white_list_misuse(self):
        project = create_project("-p-")
        misuse1 = create_misuse("-m1-", project=project)
        misuse2 = create_misuse("-m2-", project=project)
        version1 = create_version("-v1-", misuses=[misuse1], project=project)
        create_version("-v2-", misuses=[misuse2], project=project)

        self.uut.white_list = [misuse1.id]

        self.uut.process_project(project)

        assert_equals([call(project, version1)], self.uut.process_project_version.call_args_list)
