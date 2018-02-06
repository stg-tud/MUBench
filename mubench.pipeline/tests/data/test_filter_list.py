from data.filter_list import FilterList


class TestFilterList:
    def test_case_insensitive_contains(self):
        uut = FilterList(("A", "b"))
        assert uut.case_insensitive_contains("a")
        assert uut.case_insensitive_contains("B")
