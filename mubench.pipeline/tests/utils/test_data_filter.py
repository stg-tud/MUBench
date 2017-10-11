from utils.data_filter import DataFilter


class TestDataFilter:
    def test_filters_blacklisted_id(self):
        uut = DataFilter([], ["-id-"])
        assert uut.is_filtered("-id-")

    def test_does_not_filter_whitelisted_id(self):
        uut = DataFilter(["-id-"], ["-id-"])
        assert not uut.is_filtered("-id-")
