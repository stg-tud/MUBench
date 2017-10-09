from nose.tools import assert_equals

from tasks.implementations.collect_versions import CollectVersions
from tests.test_utils.data_util import create_project, create_version


class TestCollectVersions:
    def test_finds_all_versions(self):
        project = create_project("-project-")
        v1 = create_version("-v1-", project=project)
        v2 = create_version("-v2-", project=project)
        uut = CollectVersions()

        actual = uut.run(project)

        assert_equals([v1, v2], actual)
