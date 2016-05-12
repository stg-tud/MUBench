from nose.tools import assert_equals

from benchmark.datareader import DataReader
from benchmark.nosetests.test_utils.test_env_util import TestEnv


# noinspection PyAttributeOutsideInit
class TestDatareader:
    def setup(self):
        self.test_env = TestEnv()
        self.uut = DataReader(self.test_env.DATA_PATH, white_list=[""], black_list=[])

    def teardown(self):
        self.test_env.tearDown()

    def test_finds_all_files(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        self.uut.add(save_values)
        self.uut.run()
        assert len(values_used) == len(self.test_env.DATA)

    def test_correct_values_passed(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        self.uut.add(save_values)
        self.uut.run()
        assert values_used == self.test_env.DATA

    def test_return_values(self):
        def return_values(file, data): return file, data

        self.uut.add(return_values)
        actual = self.uut.run()
        assert_equals(self.test_env.DATA, actual)

    def test_black_list(self):
        def save_values(file, data): values_used.append((file, data))

        self.uut = DataReader(self.test_env.DATA_PATH, [""], [""])

        values_used = []
        self.uut.add(save_values)
        self.uut.run()

        assert not values_used

    def test_white_list(self):
        def save_values(file, data): values_used.append((file, data))

        self.uut = DataReader(self.test_env.DATA_PATH, [], [])

        values_used = []
        self.uut.add(save_values)
        self.uut.run()

        assert not values_used
