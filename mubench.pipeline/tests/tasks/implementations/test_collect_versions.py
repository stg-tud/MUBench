from nose.tools import assert_equals

from tasks.implementations.collect_versions import CollectVersionsTask
from tests.test_utils.data_util import create_project, create_version
from utils.data_entity_lists import DataEntityLists


class TestCollectVersions:
    def test_finds_all_versions(self):
        project = create_project("-project-")
        v1 = create_version("-v1-", project=project)
        v2 = create_version("-v2-", project=project)
        uut = CollectVersionsTask(DataEntityLists([], []))

        actual = uut.run(project)

        assert_equals([v1, v2], actual)

    def test_whitelisted_project(self):
        project = create_project("-project-")
        version = create_version("-id-", project=project)
        uut = CollectVersionsTask(DataEntityLists(["-project-"], []))

        actual = uut.run(project)

        assert_equals([version], actual)

    def test_whitelisted_version(self):
        project = create_project("-project-")
        version = create_version("-id-", project=project)
        uut = CollectVersionsTask(DataEntityLists(["-project-.-id-"], []))

        actual = uut.run(project)

        assert_equals([version], actual)

    def test_filters_if_not_whitelisted(self):
        project = create_project("-project-")
        create_version("-id-", project=project)
        uut = CollectVersionsTask(DataEntityLists(["-project-.-other-id-"], []))

        actual = uut.run(project)

        assert_equals([], actual)

    def test_filters_blacklisted(self):
        project = create_project("-project-")
        create_version("-id-", project=project)
        uut = CollectVersionsTask(DataEntityLists([], ["-project-.-id-"]))

        actual = uut.run(project)

        assert_equals([], actual)
