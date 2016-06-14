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

        self.pattern_file_base_name = "pattern"
        self.pattern_file_extension = ".java"
        self.pattern_file_name = self.pattern_file_base_name + self.pattern_file_extension
        self.pattern_file_path = join(self.temp_dir, self.pattern_file_name)
        create_file(self.pattern_file_path)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_fails_on_non_existent_file(self):
        uut = Pattern(self.temp_dir, "does-not-exist.java")
        assert_raises(NoPatternFileError, uut.is_valid)

    def test_fails_on_file_with_bad_extension(self):
        create_file(join(self.temp_dir, "file.txt"))
        uut = Pattern(self.temp_dir, "file.txt")
        assert_raises(NoPatternFileError, uut.is_valid)

    def test_duplicate(self):
        uut = Pattern(self.temp_dir, self.pattern_file_name)
        duplicates = uut.duplicate(self.temp_dir, 2)

        dup1path = self.pattern_file_base_name + "0" + self.pattern_file_extension
        dup2path = self.pattern_file_base_name + "1" + self.pattern_file_extension
        assert_equals(duplicates, {Pattern(self.temp_dir, dup1path), Pattern(self.temp_dir, dup2path)})
        assert exists(join(self.temp_dir, dup1path))
        assert exists(join(self.temp_dir, dup2path))

    def test_duplicate_changes_class_name(self):
        uut = Pattern(self.orig_dir, "UseResult.java")

        test_content = """
            import java.math.BigInteger;

            public class UseResult {
                public UseResult() {}
                public void pattern(String value, int bit) {}
            }
        """
        with open(uut.path, 'w') as pattern:
            pattern.write(test_content)

        duplicate = next(iter(uut.duplicate(self.temp_dir, 1)))

        with open(duplicate.path, "r") as copy:
            actual_content = copy.read()

        expectation = """
            import java.math.BigInteger;

            public class UseResult0 {
                public UseResult() {}
                public void pattern(String value, int bit) {}
            }
        """

        assert_equals(actual_content, expectation)

    def test_duplicate_with_package(self):
        pattern_name = join("mypackage", "Pattern.java")
        uut = Pattern(self.temp_dir, pattern_name)
        makedirs(uut.orig_dir)
        create_file(uut.path)

        uut.duplicate(self.temp_dir, 1)

        assert exists(join(self.temp_dir, "mypackage", "Pattern0.java"))

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
