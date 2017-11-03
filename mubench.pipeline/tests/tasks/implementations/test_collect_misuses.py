from nose.tools import assert_equals

from tasks.implementations.collect_misuses import CollectMisusesTask
from tests.test_utils.data_util import create_version, create_misuse, create_project
from utils.data_entity_lists import DataEntityLists


class TestCollectMisuses:
    def test_finds_all_misuses(self):
        m1 = create_misuse("-m1-")
        m2 = create_misuse("-m2-")
        project = create_project("-project-")
        version = create_version("-version-", misuses=[m1, m2], project=project)
        uut = CollectMisusesTask()

        actual = uut.run(version, DataEntityLists([], []))

        assert_equals([m1, m2], actual)

    def test_whitelisted_project(self):
        misuse = create_misuse("-id-")
        project = create_project("-project-")
        version = create_version("-version-", misuses=[misuse], project=project)
        uut = CollectMisusesTask()

        actual = uut.run(version, DataEntityLists(["-project-"], []))

        assert_equals([misuse], actual)

    def test_whitelisted_version(self):
        misuse = create_misuse("-id-")
        project = create_project("-project-")
        version = create_version("-version-", misuses=[misuse], project=project)
        uut = CollectMisusesTask()

        actual = uut.run(version, DataEntityLists(["-project-.-version-"], []))

        assert_equals([misuse], actual)

    def test_whitelisted(self):
        misuse = create_misuse("-id-")
        project = create_project("-project-")
        version = create_version("-version-", misuses=[misuse], project=project)
        uut = CollectMisusesTask()

        actual = uut.run(version, DataEntityLists(["-project-.-version-.-id-"], []))

        assert_equals([misuse], actual)

    def test_filters_non_whitelisted(self):
        project = create_project("-project-")
        version = create_version("-version-", misuses=[], project=project)
        create_misuse("-id-", version=version)
        uut = CollectMisusesTask()

        actual = uut.run(version, DataEntityLists(["-project-.-version-.-other-id-"], []))

        assert_equals([], actual)

    def test_filters_blacklisted(self):
        misuse = create_misuse("-id-")
        project = create_project("-project-")
        version = create_version("-version-", misuses=[misuse], project=project)
        uut = CollectMisusesTask()

        actual = uut.run(version, DataEntityLists([], ["-project-.-version-.-id-"]))

        assert_equals([], actual)
