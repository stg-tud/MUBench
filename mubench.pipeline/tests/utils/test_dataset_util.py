from nose.tools import assert_equals

from utils.dataset_util import get_white_list


def test_get_white_list_returns_empty_list_by_default():
    actual = get_white_list('', None)
    assert_equals([], actual)
