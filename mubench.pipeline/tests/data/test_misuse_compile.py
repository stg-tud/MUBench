from tempfile import mkdtemp

from nose.tools import assert_equals

from data.misuse_compile import MisuseCompile
from utils.io import remove_tree


class TestMisuseCompile:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench_misuse_compile-")

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_saves_timestamp(self):
        test_timestamp = 1516359089
        uut = MisuseCompile(self.temp_dir, [])

        uut.save(test_timestamp)

        assert_equals(test_timestamp, uut.timestamp)
