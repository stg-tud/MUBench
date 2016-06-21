from tempfile import mktemp

from os.path import join

from nose.tools import assert_equals

from benchmark.utils import csv_util
from benchmark.utils.io import remove_tree


# noinspection PyAttributeOutsideInit
class TestCsvUtil:
    def setup(self):
        self.temp_dir = mktemp(prefix="mubench-test-csv-util_")
        self.temp_file = join(self.temp_dir, "test.csv")

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_write_table(self):
        # Detector  MU1 MU2 MU3
        # D1        0   1   0
        # D2        1       0
        # D3        1   0   1

        test_content = {"D1": {"MU1": "0", "MU2": "1", "MU3": "0"},
                        "D2": {"MU1": "1", "MU3": "0"},
                        "D3": {"MU1": "1", "MU2": "0", "MU3": "1"}}

        expected_lines = ["Detector,MU1,MU2,MU3", "D1,0,1,0", "D2,1,,0", "D3,1,0,1"]
        expected = "\n".join(expected_lines)

        csv_util.write_table(self.temp_file, ["Detector", "MU1", "MU2", "MU3"], test_content)

        with open(self.temp_file, 'r') as actual_file:
            actual = actual_file.read()

        assert_equals(expected, actual)

    def test_read_table(self):
        # Detector  MU1 MU2 MU3
        # D1        0   1   0
        # D2        1       0
        # D3        1   0   1

        test_content = {"D1": {"MU1": "0", "MU2": "1", "MU3": "0"},
                        "D2": {"MU1": "1", "MU3": "0"},
                        "D3": {"MU1": "1", "MU2": "0", "MU3": "1"}}

        csv_util.write_table(self.temp_file, ["Detector", "MU1", "MU2", "MU3"], test_content)
        read_content = csv_util.read_table(self.temp_file, "Detector")

        assert_equals(test_content, read_content)
