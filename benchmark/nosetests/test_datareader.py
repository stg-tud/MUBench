from benchmark.datareader import on_all_data_do
from benchmark.nosetests.test_utils.test_env_util import TestEnv


# noinspection PyAttributeOutsideInit
class TestDatareader:
    def setup(self):
        self.test_env = TestEnv()

    def teardown(self):
        self.test_env.tearDown()

    def test_finds_all_files(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        on_all_data_do(self.test_env.DATA_PATH, save_values, white_list=[""], black_list=[])
        assert len(values_used) == len(self.test_env.DATA)

    def test_correct_values_passed(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        on_all_data_do(self.test_env.DATA_PATH, save_values, white_list=[""], black_list=[])
        assert values_used == self.test_env.DATA

    def test_return_values(self):
        def return_values(file, data): return file, data

        return_values = on_all_data_do(self.test_env.DATA_PATH, return_values, white_list=[""], black_list=[])
        assert return_values == self.test_env.DATA

    def test_black_list(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        on_all_data_do(self.test_env.DATA_PATH, save_values, white_list=[""], black_list=[""])
        assert not values_used

    def test_white_list(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        on_all_data_do(self.test_env.DATA_PATH, save_values, white_list=[], black_list=[])
        assert not values_used
