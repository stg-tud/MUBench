import unittest
from os import listdir
from os.path import join
from tempfile import gettempdir

from shutil import rmtree

import detector_runner
from config import Config
from tests.test_utils.test_env_util import TestEnvironment


class DetectorRunnerTest(unittest.TestCase):
    def setUp(self):
        self.test_env = TestEnvironment()
        detector_runner.CATCH_ERRORS = False

    def tearDown(self):
        detector_runner.CATCH_ERRORS = True
        benchmark_creates_this = join(gettempdir(), Config.CHECKOUT_DIR)
        rmtree(benchmark_creates_this, ignore_errors=True)
        self.test_env.tearDown()

    def test_run(self):
        self.assertGreater(len(self.test_env.DATA), 0, "Test data is empty")
        detector_runner.run_detector_on_all_data()
        self.assertFalse(listdir(Config.RESULTS_PATH) == [])


if __name__ == '__main__':
    unittest.main()
