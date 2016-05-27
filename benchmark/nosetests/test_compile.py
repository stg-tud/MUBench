from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.compile import Compile
from benchmark.nosetests.test_misuse import TMisuse


# noinspection PyAttributeOutsideInit
class TestCompile:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-test_")
        self.outlog = join(self.temp_dir, "out.log")
        self.errlog = join(self.temp_dir, "err.log")

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_runs_commands(self):
        called_commands = []

        def _call_mock(self: Compile, command: str): called_commands.append(command)

        uut = Compile(outlog=self.outlog, errlog=self.errlog)
        uut._call = _call_mock

    def test_uses_out_log(self):
        print_to_out_log = "echo Hallo Echo!"
        uut = Compile(outlog=self.outlog, errlog=self.errlog)
        misuse = TMisuse("", {"build": {"src": "", "commands": [print_to_out_log], "classes": ""}})

        uut.build(misuse)

        with open(self.outlog, 'r') as actual_log:
            content = actual_log.read()
            assert_equals("Hallo Echo!\n", content)

    def test_uses_err_log(self):
        print_to_err_log = ">&2 echo Hallo Echo!"
        uut = Compile(outlog=self.outlog, errlog=self.errlog)
        misuse = TMisuse("", {"build": {"src": "", "commands": [print_to_err_log], "classes": ""}})

        uut.build(misuse)

        with open(self.errlog, 'r') as actual_log:
            content = actual_log.read()
            assert_equals("Hallo Echo!\n", content)

    def test_no_fail_without_build_config(self):
        uut = Compile(outlog=self.outlog, errlog=self.errlog)
        misuse = TMisuse()
        uut.build(misuse)
