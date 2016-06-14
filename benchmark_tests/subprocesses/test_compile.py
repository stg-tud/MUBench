from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from benchmark_tests.test_utils.subprocess_util import run_on_misuse
from nose.tools import assert_equals

from benchmark.data.pattern import Pattern
from benchmark.subprocesses.compile import Compile
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import create_file
from benchmark_tests.data.test_misuse import TMisuse


# noinspection PyAttributeOutsideInit
class TestCompile:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-test_")
        self.misuse_path = join(self.temp_dir, "project")
        self.test_checkout_dir = join(self.temp_dir, "checkouts")
        self.outlog = join(self.temp_dir, "out.log")
        self.errlog = join(self.temp_dir, "err.log")

        self.call_calls = []
        self.move_calls = []
        self.copy_calls = []

        def _call_mock(a, b):
            self.call_calls.append((a, b))
            return True

        def _move_mock(a, b):
            self.move_calls.append((a, b))

        def _copy_mock(a, b):
            self.copy_calls.append((a, b))

        self.uut = Compile(self.test_checkout_dir, "checkout", "", "", "", "", 0, self.outlog, self.errlog)
        self.uut._call = _call_mock
        self.uut._move = _move_mock
        self.uut._copy = _copy_mock

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_runs_commands(self):
        misuse = TMisuse(self.misuse_path, {"build": {"src": "", "commands": ["c1", "c2", "c3"], "classes": ""}})

        run_on_misuse(self.uut, misuse)

        assert_equals(["c1", "c2", "c3"], [call[0] for call in self.call_calls])

    def test_gives_correct_cwd(self):
        misuse = TMisuse(self.misuse_path, {"build": {"src": "", "commands": ["command"], "classes": ""}})

        run_on_misuse(self.uut, misuse)

        assert_equals(join(self.test_checkout_dir, "project", "build"), self.call_calls[0][1])

    def test_no_fail_without_build_config(self):
        misuse = TMisuse(self.misuse_path)
        run_on_misuse(self.uut, misuse)

    def test_copies_project_sources(self):
        test_sources = join(self.temp_dir, "project", "checkout")
        create_file(join(test_sources, "file1.java"))
        create_file(join(test_sources, "src", "file2.java"))
        misuse = TMisuse(self.misuse_path, {"build": {"src": "src", "commands": ["command"], "classes": ""}})

        run_on_misuse(self.uut, misuse)

        self.assert_copy_in_working_directory(join("checkout", "src"), self.uut.src_normal, self.copy_calls[0])

    def test_continues_on_build_error(self):
        # noinspection PyUnusedLocal
        def _call_mock(command, cwd): return False

        self.uut._call = _call_mock
        misuse = TMisuse(self.misuse_path, {"build": {"src": "", "commands": ["command"], "classes": ""}})

        assert_equals(DataReaderSubprocess.Answer.skip, run_on_misuse(self.uut, misuse))

    def test_again_builds_with_patterns(self):
        misuse = TMisuse(self.misuse_path, {"build": {"src": "src", "commands": ["command"], "classes": "classes"}})
        misuse._PATTERNS = {Pattern("", "a")}

        run_on_misuse(self.uut, misuse)

        assert_equals(["command", "command"], [call[0] for call in self.call_calls])
        self.assert_copy_in_working_directory(
            join("build", "classes", "a.class"), join(self.uut.classes_patterns, "a.class"), self.copy_calls[3])

    def assert_copy_in_working_directory(self, source: str, target: str, copy: (str, str)):
        working_directory = join(self.test_checkout_dir, "project")
        assert_equals(join(working_directory, source), copy[0])
        assert_equals(join(working_directory, target), copy[1])

