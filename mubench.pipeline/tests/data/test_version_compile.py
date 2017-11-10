from unittest.mock import patch

from data.version_compile import VersionCompile
from nose.tools import assert_equals


@patch("data.version_compile.isdir")
class TestDependencyClasspath:
    def test_no_dependencies(self, isdir_mock):
        isdir_mock.return_value = False
        pc = VersionCompile("/base/", [])

        cp = pc.get_dependency_classpath()

        assert_equals(cp, "")

    @patch("os.listdir")
    def test_builds_classpath(self, listdir_mock, isdir_mock):
        isdir_mock.return_value = True
        listdir_mock.return_value = ["foo.jar", "bar.jar"]
        pc = VersionCompile("/base/", [])

        cp = pc.get_dependency_classpath()

        assert_equals(cp, "/base/dependencies/foo.jar:/base/dependencies/bar.jar")
