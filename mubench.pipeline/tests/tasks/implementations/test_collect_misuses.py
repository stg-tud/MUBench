from unittest.mock import MagicMock

from nose.tools import assert_equals

from tasks.implementations.collect_misuses import CollectMisusesTask
from tests.test_utils.data_util import create_version, create_misuse, create_project
from utils.data_filter import DataFilter

NO_FILTER = MagicMock()  # type: DataFilter
NO_FILTER.is_filtered = lambda id_: False


class TestCollectMisuses:
    def test_finds_all_misuses(self):
        m1 = create_misuse("-m1-")
        m2 = create_misuse("-m2-")
        version = create_version("-version-", misuses=[m1, m2])
        uut = CollectMisusesTask(NO_FILTER)

        actual = uut.run(version)

        assert_equals([m1, m2], actual)

    def test_uses_filter(self):
        misuse = create_misuse("-id-")
        project = create_project("-project-")
        version = create_version("-version-", misuses=[misuse], project=project)
        filter_ = MagicMock()  # type: DataFilter
        filter_.is_filtered = lambda id_: id_ == "-project-.-id-"
        uut = CollectMisusesTask(filter_)

        actual = uut.run(version)

        assert_equals([], actual)
