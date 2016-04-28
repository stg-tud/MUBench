import unittest

import datareader
from tests.test_utils.test_env_util import TestEnvironment


class DatareaderTest(unittest.TestCase):
    def setUp(self):
        self.test_env = TestEnvironment()

    def tearDown(self):
        self.test_env.tearDown()

    def test_finds_all_files(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        datareader.on_all_data_do(self.test_env.DATA_PATH, save_values)
        self.assertCountEqual(self.test_env.DATA, values_used)

    def test_correct_values_passed(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        datareader.on_all_data_do(self.test_env.DATA_PATH, save_values)
        self.assertListEqual(self.test_env.DATA, values_used)

    def test_return_values(self):
        def return_values(file, data): return file, data

        return_values = datareader.on_all_data_do(self.test_env.DATA_PATH, return_values)
        self.assertListEqual(self.test_env.DATA, return_values)


if __name__ == '__main__':
    unittest.main()
