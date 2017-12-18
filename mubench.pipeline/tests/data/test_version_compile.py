from tempfile import mkdtemp
from unittest.mock import patch

from shutil import rmtree

from data.version_compile import VersionCompile
from nose.tools import assert_equals


@patch("data.version_compile.isdir")
class TestDependencyClasspath:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-version-compile_")

    def teardown(self):
        rmtree(self.temp_dir)

    def test_no_dependencies(self, isdir_mock):
        isdir_mock.return_value = False
        pc = VersionCompile("/base/", "", "")

        cp = pc.get_dependency_classpath()

        assert_equals(cp, "")

    @patch("os.listdir")
    def test_builds_classpath(self, listdir_mock, isdir_mock):
        isdir_mock.return_value = True
        listdir_mock.return_value = ["foo.jar", "bar.jar"]
        pc = VersionCompile("/base/", "", "")

        cp = pc.get_dependency_classpath()

        assert_equals(cp, "/base/dependencies/foo.jar:/base/dependencies/bar.jar")

    def test_uses_zero_time_if_never_saved(self, _):
        uut = VersionCompile(self.temp_dir, "", "")
        assert_equals(0, uut.timestamp)

    def test_saves_timestamp(self, _):
        test_timestamp = 1516183458
        uut = VersionCompile(self.temp_dir, "", "")
        uut.save(test_timestamp)
        assert_equals(test_timestamp, uut.timestamp)
