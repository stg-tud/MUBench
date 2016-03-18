import unittest
from genericpath import exists
from shutil import rmtree
from tempfile import mkdtemp

from os.path import join

import logger
import settings


class LogTest(unittest.TestCase):
    def setUp(self):
        self.test_line = 'testing the logger'
        self.temp_dir = mkdtemp()
        settings.RESULTS_PATH = self.temp_dir
        settings.LOG_FILE = 'log.txt'

    def test_creates_log_file(self):
        logger.log(self.test_line)
        self.assertTrue(exists(join(settings.RESULTS_PATH, settings.LOG_FILE)))

    def test_writes_log_file(self):
        logger.log(self.test_line)
        with open(join(settings.RESULTS_PATH, settings.LOG_FILE)) as actual_file:
            self.assertEquals(actual_file.read(), self.test_line + '\n')

    def tearDown(self):
        rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
