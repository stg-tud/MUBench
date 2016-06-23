import os
from os import makedirs
from os.path import join, exists, dirname, relpath
from shutil import rmtree
from tempfile import mkdtemp
from typing import List
from unittest.mock import MagicMock, call

from nose.tools import assert_equals

from benchmark.data.pattern import Pattern
from benchmark.subprocesses.compile import Compile, CompileError
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import create_file
from benchmark_tests.data.test_misuse import create_misuse
from benchmark_tests.test_utils.subprocess_util import run_on_misuse


# noinspection PyAttributeOutsideInit
class TestCompile:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-test_")
        self.misuse_path = join(self.temp_dir, "project.id")
        self.checkout_base_path = join(self.temp_dir, "checkouts")

        self.source_dir = "src"
        self.misuse = create_misuse(self.misuse_path, {"build": {"src": self.source_dir, "commands": ["mkdir classes"], "classes": "classes"}})
        checkout = self.misuse.get_checkout(self.checkout_base_path)

        self.checkout_path = checkout.checkout_dir
        self.source_path = join(self.checkout_path, self.source_dir)
        makedirs(self.source_path)

        self.base_path = dirname(self.checkout_path)
        self.build_path = join(self.base_path, "build")

        self.call_calls = []
        self.move_calls = []
        self.copy_calls = []

        def mock_compile(commands: List[str], cwd: str):
            source_path = join(cwd, self.source_dir)
            class_path = join(cwd, "classes")
            makedirs(class_path)
            for root, dirs, files in os.walk(source_path):
                package = relpath(root, source_path)
                for file in files:
                    file = file.replace(".java", ".class")
                    create_file(join(class_path, package, file))

        self.uut = Compile(self.checkout_base_path, "original-src", "project-classes", "pattern-src", "pattern-classes", 1, "out.log", "error.log")
        self.uut._compile = MagicMock(side_effect=mock_compile)

        _call_orig = self.uut._call
        _move_orig = self.uut._move
        _copy_orig = self.uut._copy

        def _call_mock(a, b):
            print("call {} in {}".format(a, b))
            self.call_calls.append((a, b))
            return _call_orig(a, b)

        def _move_mock(a, b):
            self.move_calls.append((a, b))
            _move_orig(a, b)

        def _copy_mock(a, b):
            self.copy_calls.append((a, b))
            _copy_orig(a, b)

        self.uut._call = _call_mock
        self.uut._move = _move_mock
        self.uut._copy = _copy_mock

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_copies_original_sources(self):
        create_file(join(self.source_path, "a.file"))

        self.uut.run(self.misuse)

        assert exists(join(self.base_path, "original-src", "a.file"))

    def test_skips_copy_of_original_sources_if_copy_exists(self):
        create_file(join(self.source_path, "a.file"))
        self.uut.run(self.misuse)
        create_file(join(self.source_path, "b.file"))

        self.uut.run(self.misuse)

        assert not exists(join(self.base_path, "original-src", "b.file"))

    def test_forces_copy_of_original_sources(self):
        create_file(join(self.source_path, "a.file"))
        self.uut.run(self.misuse)
        create_file(join(self.source_path, "b.file"))
        self.uut.force_compile = True

        self.uut.run(self.misuse)

        assert exists(join(self.base_path, "original-src", "b.file"))

    def test_copies_pattern_sources(self):
        self.misuse._PATTERNS = {self.create_pattern("a.java")}

        self.uut.run(self.misuse)

        assert exists(join(self.base_path, "pattern-src", "a0.java"))

    def test_runs_commands(self):
        misuse = create_misuse(self.misuse_path, {"build": {"src": "", "commands": ["a", "b"], "classes": ""}})

        run_on_misuse(self.uut, misuse)

        self.uut._compile.assert_called_with(["a", "b"], self.build_path)

    def test_no_fail_without_build_config(self):
        misuse = create_misuse(self.misuse_path)
        run_on_misuse(self.uut, misuse)

    def test_continues_on_build_error(self):
        self.uut._compile.side_effect = CompileError("command")

        answer = self.uut.run(self.misuse)

        assert_equals(DataReaderSubprocess.Answer.skip, answer)

    def test_builds_patterns(self):
        misuse = create_misuse(self.misuse_path, {"build": {"src": "src", "commands": ["build"], "classes": "classes"}})
        misuse._PATTERNS = {self.create_pattern("a.java")}

        run_on_misuse(self.uut, misuse)

        assert_equals(self.uut._compile.mock_calls, [call(["build"], self.build_path), call(["build"], self.build_path)])
        self.assert_copy_in_working_directory(
            join("build", "classes", "a0.class"), join(self.uut.classes_patterns, "a0.class"), self.copy_calls[3])

    def test_builds_patterns_in_package(self):
        misuse = create_misuse(self.misuse_path, {"build": {"src": "src", "commands": ["mkdir classes", "mkdir classes/a", "touch classes/a/b0.class"], "classes": "classes"}})
        misuse._PATTERNS = {self.create_pattern(join("a", "b.java"))}

        run_on_misuse(self.uut, misuse)

        self.assert_copy_in_working_directory(
            join("build", "classes", "a", "b0.class"), join(self.uut.classes_patterns, "a", "b0.class"), self.copy_calls[3])

    def assert_copy_in_working_directory(self, source: str, target: str, copy: (str, str)):
        working_directory = join(self.checkout_base_path, "project", "id")
        assert_equals(join(working_directory, source), copy[0])
        assert_equals(join(working_directory, target), copy[1])

    def create_pattern(self, filename):
        pattern = Pattern(self.temp_dir, filename)
        create_file(pattern.path)
        return pattern
