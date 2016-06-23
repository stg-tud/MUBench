import os
from os import makedirs
from os.path import join, exists, dirname, relpath
from shutil import rmtree
from tempfile import mkdtemp
from typing import List
from unittest.mock import MagicMock, call

from nose.tools import assert_equals

from benchmark.data.pattern import Pattern
from benchmark.subprocesses.compile import Compile
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import create_file
from benchmark.utils.shell import CommandFailedError
from benchmark_tests.data.test_misuse import create_misuse


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
        self.original_sources_path = join(self.base_path, "original-src")
        self.original_classes_path = join(self.base_path, "original-classes")
        self.pattern_sources_path = join(self.base_path, "patterns-src")
        self.pattern_classes_path = join(self.base_path, "patterns-classes")

        def mock_compile(commands: List[str], cwd: str):
            source_path = join(cwd, self.source_dir)
            class_path = join(cwd, "classes")
            makedirs(class_path, exist_ok=True)
            for root, dirs, files in os.walk(source_path):
                package = relpath(root, source_path)
                for file in files:
                    file = file.replace(".java", ".class")
                    create_file(join(class_path, package, file))
                    print("fake compile: {}".format(join(class_path, package, file)))

        self.uut = Compile(self.checkout_base_path, 1, False)
        self.uut._compile = MagicMock(side_effect=mock_compile)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_copies_original_sources(self):
        create_file(join(self.source_path, "a.file"))

        self.uut.run(self.misuse)

        assert exists(join(self.original_sources_path, "a.file"))

    def test_skips_copy_of_original_sources_if_copy_exists(self):
        makedirs(join(self.base_path, "original-src"))
        create_file(join(self.source_path, "b.file"))

        self.uut.run(self.misuse)

        assert not exists(join(self.original_sources_path, "b.file"))

    def test_forces_copy_of_original_sources(self):
        makedirs(self.original_sources_path)
        create_file(join(self.source_path, "a.file"))
        self.uut.force_compile = True

        self.uut.run(self.misuse)

        assert exists(join(self.original_sources_path, "a.file"))

    def test_forces_clean_copy_of_original_sources(self):
        create_file(join(self.original_sources_path, "old.file"))
        self.uut.force_compile = True

        self.uut.run(self.misuse)

        assert not exists(join(self.original_sources_path, "old.file"))

    def test_copies_pattern_sources(self):
        self.misuse._PATTERNS = {self.create_pattern("a.java")}

        self.uut.run(self.misuse)

        assert exists(join(self.pattern_sources_path, "a0.java"))

    def test_skips_copy_of_pattern_sources_if_copy_exists(self):
        self.misuse._PATTERNS = {self.create_pattern("a.java")}
        self.uut.run(self.misuse)
        self.misuse._PATTERNS = {self.create_pattern("b.java")}

        self.uut.run(self.misuse)

        assert not exists(join(self.pattern_sources_path, "b0.java"))

    def test_forces_copy_of_pattern_sources(self):
        self.misuse._PATTERNS = {self.create_pattern("a.java")}
        self.uut.run(self.misuse)
        self.misuse._PATTERNS = {self.create_pattern("b.java")}
        self.uut.force_compile = True

        self.uut.run(self.misuse)

        assert exists(join(self.pattern_sources_path, "b0.java"))
        assert not exists(join(self.pattern_sources_path, "a0.java"))

    def test_continues_if_no_config(self):
        del self.misuse.meta["build"]

        answer = self.uut.run(self.misuse)

        assert_equals(DataReaderSubprocess.Answer.ok, answer)

    def test_passes_compile_commands(self):
        self.misuse.meta["build"]["commands"] = ["a", "b"]

        self.uut.run(self.misuse)

        self.uut._compile.assert_called_with(["a", "b"], self.build_path)

    def test_copies_additional_sources(self):
        create_file(join(self.misuse_path, "compile", "additional.file"))

        self.uut.run(self.misuse)

        assert exists(join(self.build_path, "additional.file"))

    def test_skips_compile_if_classes_exist(self):
        makedirs(self.original_classes_path)
        create_file(join(self.source_path, "some.file"))

        self.uut.run(self.misuse)

        assert not exists(join(self.original_classes_path, "some.file"))

    def test_forces_compile(self):
        makedirs(self.original_classes_path)
        create_file(join(self.source_path, "some.file"))
        self.uut.force_compile = True

        self.uut.run(self.misuse)

        assert exists(join(self.original_classes_path, "some.file"))

    def test_skips_on_build_error(self):
        self.uut._compile.side_effect = CommandFailedError("-cmd-", "-error message-")

        answer = self.uut.run(self.misuse)

        assert_equals(DataReaderSubprocess.Answer.skip, answer)

    def test_compiles_patterns(self):
        self.misuse._PATTERNS = {self.create_pattern("a.java")}

        self.uut.run(self.misuse)

        assert exists(join(self.pattern_classes_path, "a0.class"))

    def test_compiles_patterns_in_package(self):
        self.misuse._PATTERNS = {self.create_pattern(join("a", "b.java"))}

        self.uut.run(self.misuse)

        assert exists(join(self.pattern_classes_path, "a", "b0.class"))

    def test_skips_compile_patterns_if_pattern_classes_exist(self):
        makedirs(self.pattern_classes_path)
        self.misuse._PATTERNS = {self.create_pattern("a.java")}

        self.uut.run(self.misuse)

        assert not exists(join(self.pattern_classes_path, "a0.class"))

    def test_forces_compile_patterns(self):
        makedirs(self.pattern_classes_path)
        self.misuse._PATTERNS = {self.create_pattern("a.java")}
        self.uut.force_compile = True

        self.uut.run(self.misuse)

        assert exists(join(self.pattern_classes_path, "a0.class"))

    def create_pattern(self, filename):
        pattern = Pattern(self.temp_dir, filename)
        create_file(pattern.path)
        return pattern
