from unittest.mock import MagicMock

from nose.tools import assert_equals

from tasks.implementations.collect_versions import CollectVersions
from tests.test_utils.data_util import create_project, create_version
from utils.data_filter import DataFilter

NO_FILTER = MagicMock()  # type: DataFilter
NO_FILTER.is_filtered = lambda id_: False


class TestCollectVersions:
    def test_finds_all_versions(self):
        project = create_project("-project-")
        v1 = create_version("-v1-", project=project)
        v2 = create_version("-v2-", project=project)
        uut = CollectVersions()

        actual = uut.run(NO_FILTER, project)

        assert_equals([v1, v2], actual)

    def test_uses_filter(self):
        project = create_project("-project-")
        create_version("-id-", project=project)
        uut = CollectVersions()
        filter_ = MagicMock()  # type: DataFilter
        filter_.is_filtered = lambda id_: id_ == "-project-.-id-"

        actual = uut.run(filter_, project)

        assert_equals([], actual)
