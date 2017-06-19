from data.build_command import BuildCommand

from nose.tools import assert_equals, assert_is_instance, assert_raises
from unittest.mock import MagicMock, patch, ANY


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
