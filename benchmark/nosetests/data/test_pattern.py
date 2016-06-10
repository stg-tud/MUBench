from os import makedirs
from os.path import join, exists
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
        self.pattern_file_path = join(self.orig_dir, self.pattern_file_name)
        create_file(self.pattern_file_path)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_fails_on_non_existent_file(self):
        uut = Pattern(join(self.temp_dir, "does-not-exist.java"))
        assert_raises(NoPatternFileError, uut.is_valid)

    def test_fails_on_file_with_bad_extension(self):
        existing_file_with_bad_extension = join(self.temp_dir, "file.txt")
        create_file(existing_file_with_bad_extension)
        uut = Pattern(existing_file_with_bad_extension)
        assert_raises(NoPatternFileError, uut.is_valid)

    def test_copy_file(self):
        destination = join(self.temp_dir, "destination")
        uut = Pattern(self.pattern_file_path)
        uut.copy(destination)
        assert exists(join(destination, self.pattern_file_base_name + "0" + self.pattern_file_extension))

    def test_copy_file_twice(self):
        destination = join(self.temp_dir, "destination")
        uut = Pattern(self.pattern_file_path)
        uut.copy(destination)
        uut.copy(destination)
        assert exists(join(destination, self.pattern_file_base_name + "1" + self.pattern_file_extension))

    def test_copy_file_twice_changes_class_name(self):
        destination = join(self.temp_dir, "destination")

        test_pattern_file = join(self.orig_dir, "UseResult.java")
        test_content = ["import java.math.BigInteger;", "", "public class UseResult {",
                        "\tpublic void pattern(String value, int bit) {",
                        "\t\tBigInteger i = new BigInteger(value);",
                        "\t\ti = i.setBit(bit);",
                        "\t\treturn i;",
                        "\t}",
                        "}"]
        with open(test_pattern_file, 'w') as second_copy:
            second_copy.writelines(test_content)

        uut = Pattern(test_pattern_file)

        uut.copy(destination)
        uut.copy(destination)

        with open(join(destination, "UseResult1.java"), "r") as second_copy:
            actual_content = second_copy.read()

        assert "class UseResult1" in actual_content

    def test_duplicate(self):
        destination = join(self.temp_dir, "destination")
        uut = Pattern(self.pattern_file_path)
        uut.duplicate(destination, 5)
        assert exists(join(destination, self.pattern_file_base_name + "4" + self.pattern_file_extension))

    def test_equality(self):
        assert Pattern("a") == Pattern("a")

    def test_equality_with_other_type(self):
        Pattern("a") == 1

    def test_no_equality(self):
        assert Pattern("a") != Pattern("b")

    def test_no_equality_with_other_type(self):
        Pattern("a") != 1

    def test_to_string_is_path(self):
        assert_equals("a", str(Pattern("a")))

    def test_hashable(self):
        path = "a"
        assert_equals(hash(path), hash(Pattern(path)))
