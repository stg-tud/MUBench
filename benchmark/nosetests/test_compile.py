from os.path import join, exists
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals, assert_raises

from benchmark.compile import Compile
from benchmark.datareader import Continue
from benchmark.nosetests.test_misuse import TMisuse
from benchmark.pattern import Pattern
from benchmark.utils.io import create_file


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
        self.build_with_patterns_calls = []
        self.copy_calls = []

        def _call_mock(a, b):
            self.call_calls.append((a, b))
            return True

        def _move_mock(a, b):
            self.move_calls.append((a, b))

        def _build_with_patterns_mock(a, b, c, d, e):
            self.build_with_patterns_calls.append((a, b, c, d, e))

        def _copy_mock(a, b):
            self.copy_calls.append((a, b))

        self.uut = Compile(self.test_checkout_dir, "checkout", "", "", "", "", 0, self.outlog, self.errlog)
        self.uut._call = _call_mock
        self.uut._build_with_patterns = _build_with_patterns_mock
        self.uut._move = _move_mock
        self.uut._copy = _copy_mock

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_runs_commands(self):
        misuse = TMisuse(self.misuse_path, {"build": {"src": "", "commands": ["c1", "c2", "c3"], "classes": ""}})

        self.uut.build(misuse)

        assert_equals(["c1", "c2", "c3"], [call[0] for call in self.call_calls])

    def test_gives_correct_cwd(self):
        misuse = TMisuse(self.misuse_path, {"build": {"src": "", "commands": ["command"], "classes": ""}})

        self.uut.build(misuse)

        assert_equals(join(self.test_checkout_dir, "project", "build"), self.call_calls[0][1])

    def test_no_fail_without_build_config(self):
        misuse = TMisuse(self.misuse_path)
        self.uut.build(misuse)

    def test_copies_over_build_files(self):
        test_sources = join(self.temp_dir, "project", "checkout")
        create_file(join(test_sources, "file1.java"))
        create_file(join(test_sources, "src", "file2.java"))
        misuse = TMisuse(self.misuse_path, {"build": {"src": "", "commands": ["command"], "classes": ""}})

        self.uut.build(misuse)

        assert_equals(join(self.test_checkout_dir, "project", "checkout"), self.copy_calls[0][0])
        assert_equals(join(self.test_checkout_dir, "project", "build"), self.copy_calls[0][1])

    def test_continues_on_build_error(self):
        # noinspection PyUnusedLocal
        def _call_mock(command, cwd): return False

        self.uut._call = _call_mock
        misuse = TMisuse(self.misuse_path, {"build": {"src": "", "commands": ["command"], "classes": ""}})

        assert_raises(Continue, self.uut.build, misuse)

    def test_builds_with_patterns(self):
        @property
        def patterns_mock(self):
            return [Pattern("a")]

        misuse = TMisuse(self.misuse_path, {"build": {"src": "src", "commands": ["command"], "classes": "classes"}})

        orig_patterns = TMisuse.patterns
        try:
            TMisuse.patterns = patterns_mock

            self.uut.build(misuse)

            assert_equals(1, len(self.build_with_patterns_calls))
            actual_args = self.build_with_patterns_calls[0]

            assert_equals(["command"], actual_args[0])
            assert_equals("src", actual_args[1])
            assert_equals(join(self.test_checkout_dir, "project", "build"), actual_args[2])
            assert_equals(0, actual_args[3])
            assert_equals([Pattern("a")], actual_args[4])
        finally:
            TMisuse.patterns = orig_patterns


