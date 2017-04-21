from unittest.mock import patch

from data.project_compile import ProjectCompile
from nose.tools import assert_equals


@patch("data.project_compile.isdir")
class TestDependencyClasspath:
    def test_no_dependencies(self, isdir_mock):
        isdir_mock.return_value = False
        pc = ProjectCompile("/base/", [])

        cp = pc.get_dependency_classpath()

        assert_equals(cp, "")

    @patch("os.listdir")
    def test_builds_classpath(self, listdir_mock, isdir_mock):
        isdir_mock.return_value = True
        listdir_mock.return_value = ["foo.jar", "bar.jar"]
        pc = ProjectCompile("/base/", [])

        cp = pc.get_dependency_classpath()

        assert_equals(cp, "/base/dependencies/foo.jar:/base/dependencies/bar.jar")
