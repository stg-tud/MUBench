import unittest
from genericpath import exists
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from config import Config
from utils import logger
from utils.io import safe_open


class LogTest(unittest.TestCase):
    def setUp(self):
        self.test_line = "testing the logger"
        self.temp_dir = mkdtemp()
        Config.LOG_PATH = self.temp_dir
        Config.LOG_FILE_ERROR = join(Config.LOG_PATH, 'error.log')

    def tearDown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_creates_error_log_file(self):
        logger.log_error(self.test_line)
        self.assertTrue(exists(join(Config.LOG_PATH, Config.LOG_FILE_ERROR)))

    def test_writes_error_log_file(self):
        logger.log_error(self.test_line)
        with safe_open(Config.LOG_FILE_ERROR, 'r') as actual_file:
            self.assertEquals(self.test_line + '\n', actual_file.read())


if __name__ == '__main__':
    unittest.main()
