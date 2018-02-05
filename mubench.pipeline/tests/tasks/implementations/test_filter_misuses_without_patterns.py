from nose.tools import assert_raises

from data.pattern import Pattern
from tasks.implementations.filter_misuses_without_patterns import FilterMisusesWithoutPatternsTask
from tests.test_utils.data_util import create_misuse


class TestFilterMisusesWithoutPatternsTask:
    def test_filters_misuse_without_patterns(self):
        uut = FilterMisusesWithoutPatternsTask()
        misuse_without_patterns = create_misuse("-misuse-without-patterns-", patterns=[])
        assert_raises(UserWarning, uut.run, misuse_without_patterns)

    def test_does_not_filter_misuse_with_patterns(self):
        uut = FilterMisusesWithoutPatternsTask()
        misuse_with_patterns = create_misuse("-misuse-with-patterns-", patterns=[Pattern("-path-", "-path-")])
        uut.run(misuse_with_patterns)
