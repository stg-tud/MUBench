import unittest
from utils import dotgraph_util

TEST_LABEL = "SomePackage#SomeClass#someMethod"
TEST_LABEL_2 = "SomePackage2#SomeClass2#someMethod2"
TEST_GRAPH = ["digraph some_name {",
              "1 [label=\"{}\" shape=some_shape]".format(TEST_LABEL),
              "2 [label=\"{}\" shape=some_other_shape style=some_style]".format(TEST_LABEL_2),
              "2 -> 1 [label=\"\"]",
              "}"]
TEST_FILE_CONTENT = ["something", "---"] + TEST_GRAPH + ["---", "something else", "---"] + TEST_GRAPH


class DotGraphUtilTest(unittest.TestCase):
    def test_finds_graphs(self):
        actual = dotgraph_util.get_graphs(TEST_FILE_CONTENT)
        self.assertEquals(2, len(actual))

    def test_writes_graph_contents(self):
        actual = dotgraph_util.get_graphs(TEST_FILE_CONTENT)
        self.assertEquals([TEST_GRAPH, TEST_GRAPH], actual)

    def test_finds_labels(self):
        actual = dotgraph_util.get_labels(TEST_GRAPH)
        self.assertEquals(2, len(actual))

    def test_writes_label_contents(self):
        actual = dotgraph_util.get_labels(TEST_GRAPH)
        self.assertEquals([TEST_LABEL, TEST_LABEL_2], actual)

if __name__ == '__main__':
    unittest.main()
