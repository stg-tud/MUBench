from unittest.mock import MagicMock, call

from nose.tools import assert_equals

from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark_tests.subprocesses.test_taskrunner import create_project
from benchmark_tests.test_utils.data_util import create_version


class TestProjectVersionTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.version1 = create_version("v1")
        self.version2 = create_version("v2")
        self.project = create_project("p1", versions=[self.version1, self.version2])

        self.black_list = []
        self.white_list = []
        self.uut = ProjectVersionTask()
        self.uut.black_list = self.black_list
        self.uut.white_list = self.white_list
        self.uut.process_project_version = MagicMock()

    def test_process_version(self):
        self.uut.process_project(self.project)

        assert_equals([call(self.project, self.version1), call(self.project, self.version2)],
                      self.uut.process_project_version.call_args_list)

    def test_adds_version_to_blacklist_when_task_returns_skip(self):
        self.uut.process_project_version = MagicMock(return_value=Response.skip)

        self.uut.process_project(self.project)

        assert_equals([self.version1.id, self.version2.id], self.black_list)

    def test_skips_version_on_blacklist(self):
        self.black_list.append(self.version1.id)

        self.uut.process_project(self.project)

        assert_equals([call(self.project, self.version2)], self.uut.process_project_version.call_args_list)

    def test_skips_versions_not_on_whitelist(self):
        self.white_list.append(self.version1.id)

        self.uut.process_project(self.project)

        assert_equals([call(self.project, self.version1)], self.uut.process_project_version.call_args_list)
