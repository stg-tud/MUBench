from os import makedirs
from os.path import join, exists, dirname
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_raises, assert_equals

from benchmark.data.pattern import Pattern, NoPatternFileError
from benchmark.utils.io import create_file


class TestPattern:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-pattern-test_")
        self.orig_dir = join(join(self.temp_dir, "origin"))
        makedirs(self.orig_dir, exist_ok=True)

        self.pattern_file_name = "pattern.java"
        self.pattern_file_path = join(self.temp_dir, self.pattern_file_name)
        create_file(self.pattern_file_path)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_copy(self):
        destination = "copy"
        uut = Pattern(self.temp_dir, self.pattern_file_name)
        copy = uut.copy(join(self.temp_dir, destination))

        copy_path = join(destination, self.pattern_file_name)
        assert_equals(copy, Pattern(self.temp_dir, copy_path))
        assert exists(join(self.temp_dir, copy_path))

    def test_equality(self):
        assert Pattern("p", "a") == Pattern("p", "a")

    def test_no_equality_path(self):
        assert Pattern("a", "p") != Pattern("b", "p")

    def test_no_equality_name(self):
        assert Pattern("p", "a") != Pattern("p", "b")

    def test_to_string_is_path(self):
        assert_equals(join("a", "b"), str(Pattern("a", "b")))

    def test_hashable(self):
        path = join("a", "b")
        assert_equals(hash(path), hash(Pattern("a", "b")))
