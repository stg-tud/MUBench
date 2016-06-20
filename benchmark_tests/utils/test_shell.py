from io import StringIO

from nose.tools import assert_equals, assert_not_equals

from benchmark.utils.shell import Shell


class TestShell:
    def test_runs(self):
        uut = Shell()
        return_code = uut.exec("echo 'test'")
        assert_equals(0, return_code)

    def test_output(self):
        out = StringIO()
        uut = Shell(log=out)
        uut.exec("echo 'test'")
        assert_equals("test\n", out.getvalue())

    def test_command_failure(self):
        uut = Shell()
        return_code = uut.exec("unknown command")
        assert_not_equals(0, return_code)