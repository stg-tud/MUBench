import os

from nose.plugins.attrib import attr
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

    @attr('slow')
    def test_timeout(self):
        with assert_raises(TimeoutError):
            Shell.exec("sleep 10", timeout=1)

    def test_output_contains_non_empty_stderr(self):
        out = Shell.exec("echo 'test' 1>&2")
        expected = "=== ERROR ===" + os.linesep + "test" + os.linesep
        assert_equals(expected, out)

    def test_output_contains_stdout_and_stderr(self):
        out = Shell.exec("echo '-stdout-' && echo '-stderr-' 1>&2")
        expected = "=== OUT ===" + os.linesep + \
                   "-stdout-" + os.linesep + \
                   "=== ERROR ===" + os.linesep + \
                   "-stderr-" + os.linesep

    def test_error_contains_stderr(self):
        with assert_raises(CommandFailedError):
            Shell.exec("echo 'test' 1>&2 && exit 1")
        try:
            Shell.exec("echo 'test' 1>&2 && exit 1")
        except CommandFailedError as e:
            assert_equals("test" + os.linesep, e.error)

