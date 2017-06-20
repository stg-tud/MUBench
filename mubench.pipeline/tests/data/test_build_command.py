from data.build_command import BuildCommand, MavenCommand

from nose.tools import assert_equals, assert_is_instance, assert_raises, assert_in
from unittest.mock import MagicMock, patch, call, ANY


class BuildCommandTestImpl(BuildCommand):
    TEST_COMMAND = "-test_command-"

    @staticmethod
    def name():
        return BuildCommandTestImpl.TEST_COMMAND


class TestBuildCommand:
    def setup(self):
        self.test_subclasses = [BuildCommandTestImpl]

        self.build_command_subclasses_orig = BuildCommand.__subclasses__
        BuildCommand._get_implementations = lambda *_: self.test_subclasses

    def teardown(self):
        BuildCommand._get_implementations = self.build_command_subclasses_orig

    def test_get_correct_command(self):
        actual = BuildCommand.get(BuildCommandTestImpl.TEST_COMMAND)
        assert_is_instance(actual, BuildCommandTestImpl)

    def test_generic_command_returns_base_implementation(self):
        uut = BuildCommand.get("-some_command-")

        assert_is_instance(uut, BuildCommand)
        assert_equals("-some_command-", uut._name)

    def test_raise_on_multiple_matches(self):
        duplicate_command = BuildCommandTestImpl.TEST_COMMAND
        self.test_subclasses = [BuildCommandTestImpl, BuildCommandTestImpl]

        assert_raises(ValueError, BuildCommand.get, duplicate_command)

    @patch("data.build_command.Shell.exec")
    def test_execute_runs_command(self, shell_mock):
        uut = BuildCommand.get("-command-")

        uut.execute("-project_dir-", "-dep_dir-", "-cmp_base_path-")

        shell_mock.assert_called_with("-command-",
                                      cwd="-project_dir-", logger=ANY)

    @patch("data.build_command.Shell.exec")
    def test_execute_runs_command_with_args(self, shell_mock):
        command = "-command- -arg- --arg--"
        uut = BuildCommand.get(command)

        uut.execute("-project_dir-", "-dep_dir-", "-cmp_base_path-")

        shell_mock.assert_called_with(command,
                                      cwd="-project_dir-", logger=ANY)

    @patch("data.build_command.Shell.exec")
    def test_execute_copies_dependencies(self, shell_mock):
        shell_mock.return_value = "-output-"
        command = "-command-"
        uut = BuildCommand.get(command)
        uut._copy_dependencies = MagicMock()

        uut.execute("-project_dir-", "-dep_dir-", "-cmp_base_path-")

        uut._copy_dependencies.assert_called_with("-output-",
                                                  "-project_dir-",
                                                  "-dep_dir-",
                                                  "-cmp_base_path-")


@patch("data.build_command.shutil.copy")
@patch("data.build_command.Shell.exec")
class TestMavenCommand:
    def test_compile_with_maven(self, shell_mock, copy_mock):
        shell_mock.return_value = """
[INFO] --- maven-dependency-plugin:2.8:build-classpath (default-cli) @ testproject ---
[INFO] Dependencies classpath:
/path/dependency1.jar:/path/dependency2.jar
[INFO] ------------------------------------------------------------------------"""

        MavenCommand("mvn", ["build"]).execute("-project_dir-", "-dep_dir-", "-cmp_base_path-")

        assert_equals(shell_mock.mock_calls[0][1], ("mvn dependency:build-classpath -DincludeScope=compile build",))
        assert_in(call("/path/dependency1.jar", "-dep_dir-"), copy_mock.mock_calls)
        assert_in(call("/path/dependency2.jar",  "-dep_dir-"), copy_mock.mock_calls)

    def test_compile_with_maven_multi_modules(self, shell_mock, copy_mock):
        shell_mock.return_value = """
    [INFO] --- maven-dependency-plugin:2.8:build-classpath (default-cli) @ module1 ---
    [INFO] Dependencies classpath:
    /path/dependency1.jar
    [INFO] ------------------------------------------------------------------------
    [INFO] --- maven-dependency-plugin:2.8:build-classpath (default-cli) @ module2 ---
    [INFO] Dependencies classpath:
    /path/dependency2.jar
    [INFO] ------------------------------------------------------------------------"""

        MavenCommand("mvn", ["build"]).execute("-project_dir-", "-dep_dir-", "-cmp_base_path-")

        assert_equals(shell_mock.mock_calls[0][1], ("mvn dependency:build-classpath -DincludeScope=compile build",))
        assert_in(call("/path/dependency1.jar", "-dep_dir-"), copy_mock.mock_calls)
        assert_in(call("/path/dependency2.jar", "-dep_dir-"), copy_mock.mock_calls)

    def test_compile_with_maven_no_dependencies(self, shell_mock, copy_mock):
        shell_mock.return_value = """
[INFO] --- maven-dependency-plugin:2.8:build-classpath (default-cli) @ testproject ---
[INFO] Dependencies classpath:

[INFO] ------------------------------------------------------------------------"""

        MavenCommand("mvn", ["build"]).execute("-project_dir-", "-dep_dir-", "-cmp_base_path-")

        assert_equals(shell_mock.mock_calls[0][1], ("mvn dependency:build-classpath -DincludeScope=compile build",))


class TestGradleCommand:
    pass


class TestAntCommand:
    pass
