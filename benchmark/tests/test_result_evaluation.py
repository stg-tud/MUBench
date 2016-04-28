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


def create_result(file_result, content):
    safe_write(content, file_result, append=False)


if __name__ == '__main__':
    unittest.main()
