from os import makedirs
from os.path import join, dirname, exists
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals

from data.misuse import Misuse, Location
from data.correct_usage import CorrectUsage
from tests.test_utils.data_util import create_misuse


# noinspection PyAttributeOutsideInit
class TestMisuse:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-misuse_')

        self.project_id = "project"
        self.version_id = "version"
        self.misuse_id = "misuse1"
        self.uut = Misuse(self.temp_dir, self.project_id, self.version_id, self.misuse_id)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_extracts_id(self):
        assert self.uut.id == "project.version.misuse1"

    def test_finds_no_correct_usage(self):
        assert self.uut.correct_usages == set()

    def test_finds_single_correct_usage(self):
        expected = self.create_correct_usage_file(self.uut, "APattern.java")
        assert_equals(self.uut.correct_usages, {expected})

    def test_finds_multiple_correct_usages(self):
        correct_usage1 = self.create_correct_usage_file(self.uut, "OnePattern.java")
        correct_usage2 = self.create_correct_usage_file(self.uut, "AnotherPattern.java")
        assert_equals(self.uut.correct_usages, {correct_usage1, correct_usage2})

    def test_finds_correct_usage_in_package(self):
        correct_usage = self.create_correct_usage_file(self.uut, join("mypackage", "Pattern.java"))
        assert_equals(self.uut.correct_usages, {correct_usage})

    def test_reads_location(self):
        uut = create_misuse('', meta={"location": {"file": "file.name", "method": "foo()", "line": 42}})
        assert_equals(Location("file.name", "foo()", 42), uut.location)

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
    def create_correct_usage_file(misuse: Misuse, filename: str) -> CorrectUsage:
        correct_usages_path = join(misuse.path, "correct-usages")
        path = join(correct_usages_path, filename)
        directory = dirname(path)
        if not exists(directory):
            makedirs(directory)
        open(path, 'a').close()
        return CorrectUsage(correct_usages_path, filename)
