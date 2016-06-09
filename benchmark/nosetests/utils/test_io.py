from os import makedirs
from os.path import join, dirname, exists, isfile
from shutil import rmtree
from tempfile import mkdtemp

from benchmark.utils.io import create_file, create_file_path, safe_open, safe_write, remove_tree, copy_tree


# noinspection PyAttributeOutsideInit
class TestIo:
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
        file1 = join("dir1", "dir2", "file1")
        file2 = join("dir1", "file2")
        file3 = join("file3")
        create_file(join(self.temp_dir, file1))
        create_file(join(self.temp_dir, file2))
        create_file(join(self.temp_dir, file3))

        dst = join(self.temp_dir, "new_dir")
        copy_tree(self.temp_dir, dst)

        assert exists(join(dst, file1))
        assert exists(join(dst, file2))
        assert exists(join(dst, file3))
