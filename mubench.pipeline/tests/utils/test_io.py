from os import makedirs
from os.path import join, dirname, exists, isfile
from shutil import rmtree
from tempfile import mkdtemp

import yaml
from nose.tools import assert_raises, assert_equals

from utils.io import create_file, create_file_path, safe_open, safe_write, remove_tree, copy_tree, write_yaml


class TestIo:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp()
        self.test_file = join(self.temp_dir, 'some-subdirectory', 'some-file.txt')

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_creates_file(self):
        makedirs(dirname(self.test_file))
        create_file(self.test_file)
        assert exists(self.test_file)

    def test_creates_path(self):
        create_file_path(self.test_file)
        assert exists(dirname(self.test_file))

    def test_open_file_creates_directories_implicitly(self):
        safe_open(self.test_file, 'w+').close()
        assert isfile(self.test_file)

    def test_writes_file_safely(self):
        some_content = "Some content"
        safe_write(some_content, self.test_file, append=False)
        with open(self.test_file) as actual_file:
            assert actual_file.read() == some_content + '\n'

    def test_removes_folder_completely(self):
        create_file(join(self.temp_dir, "dir1", "dir2", "file1"))
        create_file(join(self.temp_dir, "dir1", "file2"))
        create_file(join(self.temp_dir, "file3"))

        remove_tree(self.temp_dir)

        assert not exists(self.temp_dir)

    def test_copies_tree(self):
        src = join(self.temp_dir, "src")
        file1 = join("dir1", "dir2", "file1")
        file2 = join("dir1", "file2")
        file3 = join("file3")
        create_file(join(src, file1))
        create_file(join(src, file2))
        create_file(join(src, file3))

        copy_tree(src, self.temp_dir)

        assert exists(join(self.temp_dir, file1))
        assert exists(join(self.temp_dir, file2))
        assert exists(join(self.temp_dir, file3))

    def test_copies_empty_directory(self):
        src = join(self.temp_dir, "src")
        makedirs(join(src, "empty"))

        copy_tree(src, self.temp_dir)

        assert exists(join(self.temp_dir, "empty"))

    def test_copy_creates_destination(self):
        src = join(self.temp_dir, "src")
        makedirs(src)

        dst = join(self.temp_dir, "dst")
        copy_tree(src, dst)

        assert exists(dst)

    def test_copy_fails_if_source_misssing(self):
        src = join(self.temp_dir, "src")
        with assert_raises(FileNotFoundError):
            copy_tree(src, "-irrelevant-")


class TestIOYaml:
    def test_writes_single_line(self):
        data = write_yaml({"foo": "oneliner"})
        assert_equals("foo: oneliner\n", data)

    def test_writes_multiline(self):
        data = write_yaml({"foo": "a\nb\n"})
        assert_equals("foo: |\n  a\n  b\n", data)

    def test_writes_multiline_in_dict(self):
        data = write_yaml({"foo": {"bar": "a\n"}})
        assert_equals("foo:\n  bar: |\n    a\n", data)

    def test_writes_multiline_in_list(self):
        data = write_yaml({"foo": ["a\n"]})
        assert_equals("foo:\n- |\n  a\n", data)

    def test_writes_multiline_in_dict_in_list(self):
        data = write_yaml({"foo": [{"a": "b\n"}]})
        assert_equals("foo:\n- a: |\n    b\n", data)

    def test_writes_object(self):
        class T:
            def __init__(self):
                self.f = 42

        data = write_yaml({"foo": T().__dict__})
        assert_equals("foo:\n  f: 42\n", data)

    def test_writes_dot_graph(self):
        data = write_yaml({"graph": "digraph \"foo\" {\n 1 [label=\"A\"]\n}\n"})
        assert_equals("graph: |\n  digraph \"foo\" {\n   1 [label=\"A\"]\n  }\n", data)

    def test_reads_dot_graph(self):
        data = yaml.load("graph: |\n  digraph \"foo\" {\n   1 [label=\"A\"]\n  }\n")
        assert_equals({"graph": "digraph \"foo\" {\n 1 [label=\"A\"]\n}\n"}, data)
