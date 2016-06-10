from nose.tools import assert_equals

from benchmark.utils.dotgraph_util import get_labels

TEST_LABEL = "SomePackage#SomeClass#someMethod"
TEST_LABEL_2 = "SomePackage2#SomeClass2#someMethod2"
TEST_GRAPH = 'digraph some_name {{ 1 [label="{}" shape=some_shape]  2 [label="{}" shape=some_other_shape style=some_style] 2 -> 1 [label=""] }}'.format(TEST_LABEL, TEST_LABEL_2)


def test_finds_labels():
    actual = get_labels(TEST_GRAPH)
    assert_equals([TEST_LABEL, TEST_LABEL_2], actual)
