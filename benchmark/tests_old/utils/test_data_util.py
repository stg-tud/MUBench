import unittest
from os.path import join

from benchmark.utils.data_util import extract_project_name_from_file_path, normalize_data_misuse_path, \
    normalize_result_misuse_path


class ExtractProjectNameTest(unittest.TestCase):
    def test_extract_normal_name(self):
        expected = "some-project"
        actual = extract_project_name_from_file_path(join("C:", "my-path", "{}.42-2.yml".format(expected)))
        self.assertEqual(expected, actual)

    def test_extract_synthetic_name(self):
        expected = "synthetic-case"
        actual = extract_project_name_from_file_path((join("C:", "my-path", "{}.yml".format(expected))))
        self.assertEqual(expected, actual)


class PathNormalizationTest(unittest.TestCase):
    def test_normalize_git_path_from_data(self):
        non_normalized_path = r'src/main/java/com/alibaba/druid/filter/config/ConfigTools.java'
        expected_normalized_path = r'src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
        actual_normalized_path = normalize_data_misuse_path(non_normalized_path)
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_svn_path_from_data(self):
        non_normalized_path = r'incubator/jackrabbit/trunk/src/java/org/apache/jackrabbit/core/state/obj/ObjectPersistenceManager.java'
        expected_normalized_path = r'src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
        actual_normalized_path = normalize_data_misuse_path(non_normalized_path)
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_synthetic_path_from_data(self):
        non_normalized_path = r'synthetic-androidactivity-1.java'
        expected_normalized_path = r'synthetic-androidactivity-1.java'
        actual_normalized_path = normalize_data_misuse_path(non_normalized_path)
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_git_path_from_result(self):
        non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\alibaba-druid\src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
        expected_normalized_path = r'src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
        actual_normalized_path = normalize_result_misuse_path(non_normalized_path,
                                                              r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark')
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_svn_path_from_result(self):
        non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\jackrabbit\trunk\src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
        expected_normalized_path = r'src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
        actual_normalized_path = normalize_result_misuse_path(non_normalized_path,
                                                              r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark')
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_synthetic_path_from_result(self):
        non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\synthetic-androidactivity-1\synthetic-androidactivity-1.java'
        expected_normalized_path = r'synthetic-androidactivity-1.java'
        actual_normalized_path = normalize_result_misuse_path(non_normalized_path,
                                                              r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark')
        self.assertEquals(expected_normalized_path, actual_normalized_path)


if __name__ == '__main__':
    unittest.main()
