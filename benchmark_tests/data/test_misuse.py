from os import makedirs
from os.path import join, dirname, exists
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.data.misuse import Misuse
from benchmark.data.pattern import Pattern
from benchmark_tests.test_utils.data_util import create_misuse


# noinspection PyAttributeOutsideInit
class TestMisuse:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-misuse_')

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_extracts_id(self):
        uut = Misuse("/MUBench/data/project/misuses/id")
        assert uut.id == "id"

    def test_finds_no_pattern(self):
        uut = Misuse(self.temp_dir)
        assert uut.patterns == set()

    def test_finds_single_pattern(self):
        uut = Misuse(self.temp_dir)
        expected = self.create_pattern_file(uut, "APattern.java")
        assert_equals(uut.patterns, {expected})

    def test_finds_multiple_patterns(self):
        uut = Misuse(self.temp_dir)
        pattern1 = self.create_pattern_file(uut, "OnePattern.java")
        pattern2 = self.create_pattern_file(uut, "AnotherPattern.java")
        assert_equals(uut.patterns, {pattern1, pattern2})

    def test_finds_pattern_in_package(self):
        uut = Misuse(self.temp_dir)
        pattern = self.create_pattern_file(uut, join("mypackage", "Pattern.java"))
        assert_equals(uut.patterns, {pattern})

    def test_reads_usage(self):
        uut = create_misuse('', yaml={"usage": "test-usage"})
        assert_equals("test-usage", uut.usage)

    def test_reads_files(self):
        uut = create_misuse('', yaml={"fix": {"files": [{"name": "file1"}, {"name": "file2"}]}})
        assert_equals(["file1", "file2"], uut.files)

    def test_equals_by_path(self):
        assert Misuse("foo/bar") == Misuse("foo/bar")

    def test_differs_by_path(self):
        assert Misuse("foo/bar") != Misuse("bar/bazz")

    @staticmethod
    def create_pattern_file(misuse: Misuse, filename: str) -> Pattern:
        patterns_path = join(misuse.path, "patterns")
        path = join(patterns_path, filename)
        directory = dirname(path)
        if not exists(directory):
            makedirs(directory)
        open(path, 'a').close()
        return Pattern(patterns_path, filename)
