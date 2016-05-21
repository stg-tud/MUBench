from benchmark.utils.dotgraph_util import get_graphs, get_labels

TEST_LABEL = "SomePackage#SomeClass#someMethod"
TEST_LABEL_2 = "SomePackage2#SomeClass2#someMethod2"
TEST_GRAPH = [" digraph some_name {",
              "1 [label=\"{}\" shape=some_shape]".format(TEST_LABEL),
              "2 [label=\"{}\" shape=some_other_shape style=some_style]".format(TEST_LABEL_2),
              "2 -> 1 [label=\"\"]",
              "}"]
TEST_GRAPH_2 = ["1 [label=\"{}\"]".format(TEST_LABEL) + " 2 [label=\"{}\"]".format(TEST_LABEL_2)]
TEST_FILE_CONTENT = ["something", "---"] + TEST_GRAPH + ["---", "something else", "---"] + TEST_GRAPH


def test_finds_graph():
    actual = get_graphs(TEST_FILE_CONTENT)
    assert actual == [TEST_GRAPH, TEST_GRAPH]


def test_finds_labels():
    actual = get_labels(TEST_GRAPH)
    assert actual == [TEST_LABEL, TEST_LABEL_2]


def test_finds_labels_in_single_line_graph():
    actual = get_labels(TEST_GRAPH)
    assert actual == [TEST_LABEL, TEST_LABEL_2]
