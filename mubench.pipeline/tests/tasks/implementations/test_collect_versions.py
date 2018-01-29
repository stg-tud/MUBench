from unittest.mock import patch, PropertyMock

from nose.tools import assert_equals

from tasks.implementations.collect_versions import CollectVersionsTask
from tests.test_utils.data_util import create_project, create_version
from utils.data_entity_lists import DataEntityLists


class TestCollectVersions:
    def test_finds_all_versions(self):
        project = create_project("-project-")
        v1 = create_version("-v1-", project=project)
        v2 = create_version("-v2-", project=project)
        uut = CollectVersionsTask(False)

        actual = uut.run(project, DataEntityLists([], []))

        assert_equals([v1, v2], actual)

    def test_whitelisted_project(self):
        project = create_project("-project-")
        version = create_version("-id-", project=project)
        uut = CollectVersionsTask(False)

        actual = uut.run(project, DataEntityLists(["-project-"], []))

        assert_equals([version], actual)

    def test_whitelisted_version(self):
        project = create_project("-project-")
        version = create_version("-id-", project=project)
        uut = CollectVersionsTask(False)

        actual = uut.run(project, DataEntityLists(["-project-.-id-"], []))

        assert_equals([version], actual)

    def test_filters_if_not_whitelisted(self):
        project = create_project("-project-")
        create_version("-id-", project=project)
        uut = CollectVersionsTask(False)

        actual = uut.run(project, DataEntityLists(["-project-.-other-id-"], []))

        assert_equals([], actual)

    def test_filters_blacklisted(self):
        project = create_project("-project-")
        create_version("-id-", project=project)
        uut = CollectVersionsTask(False)

        actual = uut.run(project, DataEntityLists([], ["-project-.-id-"]))

        assert_equals([], actual)

    @patch("data.project_version.ProjectVersion.is_compilable", new_callable=PropertyMock)
    def test_filters_not_compilable(self, version_is_compilable_mock):
        project = create_project("-project-")
        create_version("-id-", project=project)
        version_is_compilable_mock.return_value = False
        uut = CollectVersionsTask(True)

        actual = uut.run(project, DataEntityLists([], []))

        assert_equals([], actual)
