import os

from nose.tools import assert_equals, assert_raises

from utils.shell import Shell, CommandFailedError


class TestShell:
    def test_runs(self):
        Shell.exec("echo 'test'")

    def test_output(self):
        out = Shell.exec("echo test")
        assert_equals("test" + os.linesep, out)

    def test_command_failure(self):
        with assert_raises(CommandFailedError):
            Shell.exec("unknown command")

    def test_command_try(self):
        assert Shell.try_exec("echo 'test'")

    def test_command_try_failure(self):
        assert not Shell.try_exec("unknown command")

    def test_timeout(self):
        with assert_raises(TimeoutError):
            Shell.exec("sleep 10", timeout=1)
