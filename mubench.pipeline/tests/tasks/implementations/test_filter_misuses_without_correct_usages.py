from nose.tools import assert_raises

from data.correct_usage import CorrectUsage
from tasks.implementations.filter_misuses_without_correct_usages import FilterMisusesWithoutCorrectUsagesTask
from tests.test_utils.data_util import create_misuse


class TestFilterMisusesWithoutCorrectUsagesTask:
    def test_filters_misuse_without_correct_usages(self):
        uut = FilterMisusesWithoutCorrectUsagesTask()
        misuse_without_correct_usages = create_misuse("-misuse-without-correct_usages-", correct_usages=[])
        assert_raises(UserWarning, uut.run, misuse_without_correct_usages)

    def test_does_not_filter_misuse_with_correct_usages(self):
        uut = FilterMisusesWithoutCorrectUsagesTask()
        misuse_with_correct_usages = create_misuse("-misuse-with-correct_usages-", correct_usages=[CorrectUsage("-path-", "-path-")])
        uut.run(misuse_with_correct_usages)
