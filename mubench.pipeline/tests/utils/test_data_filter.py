from utils.data_filter import DataFilter


class TestDataFilter:
    def test_filters_blacklisted_id(self):
        uut = DataFilter([], ["-id-"])
        assert uut.is_filtered("-id-")

    def test_filters_non_whitelisted_id(self):
        uut = DataFilter(["-other-id-"], [])
        assert uut.is_filtered("-id-")

    def test_filters_blacklisted_and_whitelisted_id(self):
        uut = DataFilter(["-id-"], ["-id-"])
        assert uut.is_filtered("-id-")

    def test_whitelisting_misuse_also_whitelists_its_version(self):
        uut = DataFilter(["-project-.-version-.-misuse-"], [])
        assert not uut.is_filtered("-project-.-version-")

    def test_whitelisting_projects_also_whitelists_its_versions(self):
        uut = DataFilter(["-project-"], [])
        assert not uut.is_filtered("-project-.-version-")

    def test_filters_suffixes_of_whitelisted_prefixes(self):
        uut = DataFilter(["-project-.-version-"], [])
        assert uut.is_filtered("-project-.-other-version-")

    def test_filters_blacklisted_by_prefix(self):
        uut = DataFilter([], ["-project-"])
        assert uut.is_filtered("-project-.-version-")
