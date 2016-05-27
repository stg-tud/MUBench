from os.path import join, exists
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.compile import Compile
from benchmark.nosetests.test_misuse import TMisuse


from benchmark.utils.io import create_file


# noinspection PyAttributeOutsideInit
class TestCompile:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-test_")
        self.test_checkout_dir = join(self.temp_dir, "checkouts")
        self.outlog = join(self.temp_dir, "out.log")
        self.errlog = join(self.temp_dir, "err.log")

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_runs_commands(self):
        called_commands = []

        def _call_mock(command: str): called_commands.append(command)

        uut = Compile(checkout_base_dir=self.test_checkout_dir, outlog=self.outlog, errlog=self.errlog)
        uut._call = _call_mock

        misuse = TMisuse(self.temp_dir, {"build": {"src": "", "commands": ["c1", "c2", "c3"], "classes": ""}})

        uut.build(misuse)

        assert_equals(["c1", "c2", "c3"], called_commands)

    def test_uses_out_log(self):
        print_to_out_log = "echo Hallo Echo!"
        uut = Compile(checkout_base_dir=self.test_checkout_dir, outlog=self.outlog, errlog=self.errlog)
        misuse = TMisuse(self.temp_dir, {"build": {"src": "", "commands": [print_to_out_log], "classes": ""}})

        uut.build(misuse)

        with open(self.outlog, 'r') as actual_log:
            content = actual_log.read()
            assert_equals("Hallo Echo!\n", content)

    def test_uses_err_log(self):
        print_to_err_log = ">&2 echo Hallo Echo!"
        uut = Compile(checkout_base_dir=self.test_checkout_dir, outlog=self.outlog, errlog=self.errlog)
        misuse = TMisuse(self.temp_dir, {"build": {"src": "", "commands": [print_to_err_log], "classes": ""}})

        uut.build(misuse)

        with open(self.errlog, 'r') as actual_log:
            content = actual_log.read()
            assert_equals("Hallo Echo!\n", content)

    def test_no_fail_without_build_config(self):
        uut = Compile(checkout_base_dir=self.test_checkout_dir, outlog=self.outlog, errlog=self.errlog)
        misuse = TMisuse(join(self.temp_dir, "project"))
        uut.build(misuse)

    def test_copies_over_build_files(self):
        test_sources = join(self.temp_dir, "project", "compile")
        create_file(join(test_sources, "file1.java"))
        create_file(join(test_sources, "src", "file2.java"))

        uut = Compile(checkout_base_dir=self.test_checkout_dir, outlog=self.outlog, errlog=self.errlog)

        misuse = TMisuse(join(self.temp_dir, "project"))

        uut.build(misuse)

        assert exists(join(self.test_checkout_dir, "project", "file1.java"))
        assert exists(join(self.test_checkout_dir, "project", "src", "file2.java"))