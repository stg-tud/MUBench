import os
import unittest

from os.path import join
from tempfile import gettempdir

import result_evaluation
from config import Config
from tests.test_utils.test_env_util import TestEnvironment
from utils.io import safe_write


class ResultsTest(unittest.TestCase):
    def setUp(self):
        self.test_env = TestEnvironment()

        self.file_result_git = join(Config.RESULTS_PATH, 'git', Config.FILE_DETECTOR_RESULT)
        self.file_result_svn = join(Config.RESULTS_PATH, 'svn', Config.FILE_DETECTOR_RESULT)

    def tearDown(self):
        self.test_env.tearDown()

    def test_correct_total(self):
        create_result(self.file_result_git, '')
        create_result(self.file_result_svn, 'File: some-class.java')
        actual_results = result_evaluation.evaluate_results()
        self.assertEquals(3, actual_results[0])

    def test_correct_applied(self):
        create_result(self.file_result_git, '')
        create_result(self.file_result_svn, 'File: some-class.java')
        actual_results = result_evaluation.evaluate_results()
        self.assertEquals(2, actual_results[1])

    def test_correct_found(self):
        create_result(self.file_result_git, '')
        create_result(self.file_result_svn, 'File: some-class.java')
        actual_results = result_evaluation.evaluate_results()
        self.assertEquals(1, actual_results[2])

    def test_uses_digraph(self):
        create_result(self.file_result_git,
                      'File: some-class.java' + os.linesep + '---' + os.linesep + 'digraph name {' + os.linesep +
                      '1 [label="{}"]'.format(self.test_env.git_misuse_label) +
                      os.linesep + '}')
        actual_results = result_evaluation.evaluate_results()
        self.assertEquals(1, actual_results[2])


class PathNormalizationTest(unittest.TestCase):
    def setUp(self):
        Config.CHECKOUT_DIR = join(gettempdir(), 'MUBenchmark')

    def test_normalize_git_path_from_data(self):
        non_normalized_path = r'src/main/java/com/alibaba/druid/filter/config/ConfigTools.java'
        expected_normalized_path = r'src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
        actual_normalized_path = result_evaluation.normalize_data_misuse_path(non_normalized_path)
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_svn_path_from_data(self):
        non_normalized_path = r'incubator/jackrabbit/trunk/src/java/org/apache/jackrabbit/core/state/obj/ObjectPersistenceManager.java'
        expected_normalized_path = r'src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
        actual_normalized_path = result_evaluation.normalize_data_misuse_path(non_normalized_path)
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_synthetic_path_from_data(self):
        non_normalized_path = r'synthetic-androidactivity-1.java'
        expected_normalized_path = r'synthetic-androidactivity-1.java'
        actual_normalized_path = result_evaluation.normalize_data_misuse_path(non_normalized_path)
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_git_path_from_result(self):
        non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\alibaba-druid\src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
        expected_normalized_path = r'src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
        actual_normalized_path = result_evaluation.normalize_result_misuse_path(non_normalized_path)
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_svn_path_from_result(self):
        non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\jackrabbit\trunk\src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
        expected_normalized_path = r'src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
        actual_normalized_path = result_evaluation.normalize_result_misuse_path(non_normalized_path)
        self.assertEquals(expected_normalized_path, actual_normalized_path)

    def test_normalize_synthetic_path_from_result(self):
        non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\synthetic-androidactivity-1\synthetic-androidactivity-1.java'
        expected_normalized_path = r'synthetic-androidactivity-1.java'
        actual_normalized_path = result_evaluation.normalize_result_misuse_path(non_normalized_path)
        self.assertEquals(expected_normalized_path, actual_normalized_path)


def create_result(file_result, content):
    safe_write(content, file_result, append=False)


if __name__ == '__main__':
    unittest.main()
