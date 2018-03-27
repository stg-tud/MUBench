from os import makedirs
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals

from data.correct_usage import CorrectUsage
from utils.io import create_file


class TestCorrectUsage:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-correct_usage-test_")
        self.orig_dir = join(join(self.temp_dir, "origin"))
        makedirs(self.orig_dir, exist_ok=True)

        self.correct_usage_file_name = "correct_usage.java"
        self.correct_usage_file_path = join(self.temp_dir, self.correct_usage_file_name)
        create_file(self.correct_usage_file_path)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_equality(self):
        assert CorrectUsage("p", "a") == CorrectUsage("p", "a")

    def test_no_equality_path(self):
        assert CorrectUsage("a", "p") != CorrectUsage("b", "p")

    def test_no_equality_name(self):
        assert CorrectUsage("p", "a") != CorrectUsage("p", "b")

    def test_to_string_is_path(self):
        assert_equals(join("a", "b"), str(CorrectUsage("a", "b")))

    def test_hashable(self):
        path = join("a", "b")
        assert_equals(hash(path), hash(CorrectUsage("a", "b")))

    def test_path(self):
        correct_usage = CorrectUsage("/base", "correct_usage")

        assert_equals("/base/correct_usage", correct_usage.path)

    def test_name(self):
        correct_usage = CorrectUsage("/base", "path/correct_usage.file")

        assert_equals("correct_usage", correct_usage.name)

    def test_relative_path_without_extension(self):
        correct_usage = CorrectUsage("/base", "path/correct_usage.file")

        assert_equals("path/correct_usage", correct_usage.relative_path_without_extension)
