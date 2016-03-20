import unittest
from genericpath import isfile, exists
from os import makedirs
from os.path import join, dirname
from shutil import rmtree
from tempfile import mkdtemp

import utils.io


class IoTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = mkdtemp()
        self.test_file = join(self.temp_dir, 'some-subdirectory', 'some-file.txt')

    def test_creates_file(self):
        makedirs(dirname(self.test_file))
        utils.io.create_file(self.test_file)
        self.assertTrue(exists(self.test_file))

    def test_creates_path(self):
        utils.io.create_file_path(self.test_file)
        self.assertTrue(exists(self.test_file))

    def test_open_file_creates_directories_implicitly(self):
        utils.io.safe_open(self.test_file, 'r+').close()
        self.assertTrue(isfile(self.test_file))

    def test_writes_file_safely(self):
        some_content = "Some content"
        utils.io.safe_write(some_content, self.test_file, append=False)
        with open(self.test_file) as actual_file:
            self.assertEquals(some_content + '\n', actual_file.read())

    def tearDown(self):
        rmtree(self.temp_dir)


if __name__ == '__main__':
    unittest.main()
