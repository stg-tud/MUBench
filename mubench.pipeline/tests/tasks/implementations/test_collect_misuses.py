from nose.tools import assert_equals

from tasks.implementations.collect_misuses import CollectMisuses
from tests.test_utils.data_util import create_version, create_misuse


class TestCollectMisuses:
    def test_finds_all_versions(self):
        m1 = create_misuse("-m1-")
        m2 = create_misuse("-m2-")
        version = create_version("-version-", misuses=[m1, m2])
        uut = CollectMisuses()

        actual = uut.run(version)

        assert_equals([m1, m2], actual)
