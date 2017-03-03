from os import makedirs
from os.path import join, dirname, exists
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals

from data.misuse import Misuse, Location
from data.pattern import Pattern
from tests.test_utils.data_util import create_misuse


# noinspection PyAttributeOutsideInit
class TestMisuse:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-misuse_')

        self.project_id = "project"
        self.misuse_id = "misuse1"
        self.uut = Misuse(self.temp_dir, self.project_id, self.misuse_id)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_extracts_id(self):
        assert self.uut.id == "project.misuse1"

    def test_finds_no_pattern(self):
        assert self.uut.patterns == set()

    def test_finds_single_pattern(self):
        expected = self.create_pattern_file(self.uut, "APattern.java")
        assert_equals(self.uut.patterns, {expected})

    def test_finds_multiple_patterns(self):
        pattern1 = self.create_pattern_file(self.uut, "OnePattern.java")
        pattern2 = self.create_pattern_file(self.uut, "AnotherPattern.java")
        assert_equals(self.uut.patterns, {pattern1, pattern2})

    def test_finds_pattern_in_package(self):
        pattern = self.create_pattern_file(self.uut, join("mypackage", "Pattern.java"))
        assert_equals(self.uut.patterns, {pattern})

    def test_reads_location(self):
        uut = create_misuse('', meta={"location": {"file": "file.name", "method": "foo()"}})
        assert_equals(Location("file.name", "foo()"), uut.location)

    def test_reads_description(self):
        misuse = create_misuse("", meta={"description": "bla bla bla"})
        assert_equals("bla bla bla", misuse.description)

    def test_reads_fix(self):
        misuse = create_misuse("",
                               meta={"fix": {"commit": "http://link.to/commit", "description": "blub", "revision": 42}})
        assert_equals("http://link.to/commit", misuse.fix.commit)
        assert_equals("blub", misuse.fix.description)
        assert_equals("42", misuse.fix.revision)

    @staticmethod
    def create_pattern_file(misuse: Misuse, filename: str) -> Pattern:
        patterns_path = join(misuse.path, "patterns")
        path = join(patterns_path, filename)
        directory = dirname(path)
        if not exists(directory):
            makedirs(directory)
        open(path, 'a').close()
        return Pattern(patterns_path, filename)
