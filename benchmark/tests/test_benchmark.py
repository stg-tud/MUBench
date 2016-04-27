import unittest
from os import listdir
from os.path import join
from tempfile import gettempdir

from shutil import rmtree

import benchmark
from config import Config
from tests.test_utils.test_env_util import TestEnvironment


class BenchmarkTest(unittest.TestCase):
    def setUp(self):
        self.test_env = TestEnvironment()
        benchmark.CATCH_ERRORS = False

    def tearDown(self):
        benchmark.CATCH_ERRORS = True
        benchmark_creates_this = join(gettempdir(), Config.CHECKOUT_DIR)
        rmtree(benchmark_creates_this, ignore_errors=True)
        self.test_env.tearDown()

    def test_run(self):
        self.assertGreater(len(self.test_env.DATA), 0, "Test data is empty")
        for data in self.test_env.DATA:
            benchmark.analyze(data[0], data[1])
        self.assertFalse(listdir(Config.RESULTS_PATH) == [])


class ExtractProjectNameTest(unittest.TestCase):
    def test_extract_normal_name(self):
        expected = "some-project"
        actual = benchmark.extract_project_name_from_file_path(join("C:", "my-path", "{}.42-2.yml".format(expected)))
        self.assertEqual(expected, actual)

    def test_extract_synthetic_name(self):
        expected = "synthetic-case"
        actual = benchmark.extract_project_name_from_file_path((join("C:", "my-path", "{}.yml".format(expected))))
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
