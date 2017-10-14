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

    def test_whitelists_by_prefix(self):
        uut = DataFilter(["-project-"], [])
        assert not uut.is_filtered("-project-.-version-")
