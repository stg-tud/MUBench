from os import makedirs
from os.path import join, dirname, exists, isfile
from shutil import rmtree
from tempfile import mkdtemp

from benchmark.utils.io import create_file, create_file_path, safe_open, safe_write


# noinspection PyAttributeOutsideInit
class TestIo:
    def setup(self):
        self.temp_dir = mkdtemp()
        self.test_file = join(self.temp_dir, 'some-subdirectory', 'some-file.txt')

    def teardown(self):
        rmtree(self.temp_dir)

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
