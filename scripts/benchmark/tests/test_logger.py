import unittest
from genericpath import exists
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

import logger
import settings


class LogTest(unittest.TestCase):
    def setUp(self):
        self.test_line = 'testing the logger'
        self.temp_dir = mkdtemp()
        settings.LOG_FILE = join(self.temp_dir, 'log.txt')

    def test_creates_log_file(self):
        logger.log(self.test_line)
        self.assertTrue(exists(settings.LOG_FILE))

    def test_writes_log_file(self):
        logger.log(self.test_line)
        with open(settings.LOG_FILE) as actual_file:
            self.assertEquals(actual_file.read(), self.test_line + '\n')

    def tearDown(self):
        rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
