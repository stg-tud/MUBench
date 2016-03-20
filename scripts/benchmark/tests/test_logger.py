import unittest
from genericpath import exists
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

import settings
from utils import logger
from utils.io import safe_open


class LogTest(unittest.TestCase):
    def setUp(self):
        self.test_line = "testing the logger"
        self.temp_dir = mkdtemp()
        settings.LOG_PATH = self.temp_dir
        settings.LOG_FILE_ERROR = join(settings.LOG_PATH, 'error.log')

    def test_creates_error_log_file(self):
        logger.log_error(self.test_line)
        self.assertTrue(exists(join(settings.LOG_PATH, settings.LOG_FILE_ERROR)))

    def test_writes_error_log_file(self):
        logger.log_error(self.test_line)
        with safe_open(settings.LOG_FILE_ERROR) as actual_file:
            self.assertEquals(self.test_line + '\n', actual_file.read())

    def tearDown(self):
        rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
