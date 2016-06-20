from io import StringIO

from nose.tools import assert_equals, assert_raises

from benchmark.utils.shell import Shell, CommandFailedError


class TestShell:
    def test_runs(self):
        uut = Shell()
        uut.exec("echo 'test'")

    def test_output(self):
        out = StringIO()
        uut = Shell(log=out)
        uut.exec("echo 'test'")
        assert_equals("test\n", out.getvalue())

    def test_command_failure(self):
        uut = Shell()
        with assert_raises(CommandFailedError):
            uut.exec("unknown command")

    def test_command_try(self):
        uut = Shell()
        assert uut.try_exec("echo 'test'")

    def test_command_try_failure(self):
        uut = Shell()
        assert not uut.try_exec("unknown command")
