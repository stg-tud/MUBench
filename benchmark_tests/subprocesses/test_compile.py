from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from os import makedirs

from benchmark_tests.test_utils.subprocess_util import run_on_misuse
from nose.tools import assert_equals

from benchmark.data.pattern import Pattern
from benchmark.subprocesses.compile import Compile
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import create_file
from benchmark_tests.data.test_misuse import create_misuse


# noinspection PyAttributeOutsideInit
class TestCompile:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-test_")
        self.misuse_path = join(self.temp_dir, "project.id")
        self.test_checkout_dir = join(self.temp_dir, "checkouts")
        self.outlog = "out.log"
        self.errlog = "err.log"

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

        self.uut = Compile(self.test_checkout_dir, "project-src", "project-classes", "pattern-src", "pattern-classes", 1, self.outlog, self.errlog)
        self.uut._call = _call_mock
        self.uut._move = _move_mock
        self.uut._copy = _copy_mock

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_runs_commands(self):
        misuse = create_misuse(self.misuse_path, {"build": {"src": "", "commands": ["c1", "c2", "c3"], "classes": ""}})

        run_on_misuse(self.uut, misuse)

        assert_equals(["c1", "c2", "c3"], [call[0] for call in self.call_calls])

    def test_gives_correct_cwd(self):
        misuse = create_misuse(self.misuse_path, {"build": {"src": "", "commands": ["command"], "classes": ""}})

        run_on_misuse(self.uut, misuse)

        assert_equals(join(self.test_checkout_dir, "project", "id", "build"), self.call_calls[0][1])

    def test_no_fail_without_build_config(self):
        misuse = create_misuse(self.misuse_path)
        run_on_misuse(self.uut, misuse)

    def test_copies_project_sources(self):
        test_sources = join(self.temp_dir, "project", "checkout")
        create_file(join(test_sources, "file1.java"))
        create_file(join(test_sources, "src", "file2.java"))
        misuse = create_misuse(self.misuse_path, {"build": {"src": "src", "commands": ["command"], "classes": ""}})

        run_on_misuse(self.uut, misuse)

        self.assert_copy_in_working_directory(join("checkout", "src"), self.uut.src_normal, self.copy_calls[0])

    def test_continues_on_build_error(self):
        # noinspection PyUnusedLocal
        def _call_mock(command, cwd): return False

        self.uut._call = _call_mock
        misuse = create_misuse(self.misuse_path, {"build": {"src": "", "commands": ["command"], "classes": ""}})

        assert_equals(DataReaderSubprocess.Answer.skip, run_on_misuse(self.uut, misuse))

    def test_builds_patterns(self):
        misuse = create_misuse(self.misuse_path, {"build": {"src": "src", "commands": ["command"], "classes": "classes"}})
        pattern = Pattern(self.temp_dir, "a")
        create_file(pattern.path)
        misuse._PATTERNS = {pattern}

        run_on_misuse(self.uut, misuse)

        assert_equals(["command", "command"], [call[0] for call in self.call_calls])
        self.assert_copy_in_working_directory(
            join("build", "classes", "a0.class"), join(self.uut.classes_patterns, "a0.class"), self.copy_calls[3])

    def test_builds_patterns_in_package(self):
        misuse = create_misuse(self.misuse_path, {"build": {"src": "src", "commands": ["command"], "classes": "classes"}})
        pattern = Pattern(self.temp_dir, join("a", "b.java"))
        makedirs(pattern.orig_dir)
        create_file(pattern.path)
        misuse._PATTERNS = {pattern}

        run_on_misuse(self.uut, misuse)

        assert_equals(["command", "command"], [call[0] for call in self.call_calls])
        self.assert_copy_in_working_directory(
            join("build", "classes", "a", "b0.class"), join(self.uut.classes_patterns, "a", "b0.class"), self.copy_calls[3])

    def assert_copy_in_working_directory(self, source: str, target: str, copy: (str, str)):
        working_directory = join(self.test_checkout_dir, "project", "id")
        assert_equals(join(working_directory, source), copy[0])
        assert_equals(join(working_directory, target), copy[1])
