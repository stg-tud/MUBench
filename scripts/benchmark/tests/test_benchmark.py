import unittest
from os import listdir
from os.path import join
from tempfile import gettempdir

from shutil import rmtree

import benchmark
from tests.test_utils.test_env_util import TestEnvironment


class BenchmarkTest(unittest.TestCase):
    def setUp(self):
        self.test_env = TestEnvironment()
        benchmark.CATCH_ERRORS = False

    def test_run(self):
        self.assertGreater(len(self.test_env.DATA), 0, "Test data is empty")
        for data in self.test_env.DATA:
            benchmark.analyze(data[0], data[1])
        self.assertFalse(listdir(self.test_env.RESULTS_PATH) == [])

    def tearDown(self):
        benchmark.CATCH_ERRORS = True
        benchmark_creates_this = join(gettempdir(), self.test_env.TEMP_SUBFOLDER)
        rmtree(benchmark_creates_this, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
