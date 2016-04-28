import os
import unittest
from os.path import join

import result_evaluation
from tests.test_utils.test_env_util import TestEnvironment
from utils.io import safe_write


class ResultsTest(unittest.TestCase):
    def setUp(self):
        self.test_env = TestEnvironment()

        self.file_result_git = join(self.test_env.CONFIG.RESULTS_PATH,
                                    'git',
                                    self.test_env.CONFIG.DETECTOR,
                                    self.test_env.CONFIG.FILE_DETECTOR_RESULT)
        self.file_result_svn = join(self.test_env.CONFIG.RESULTS_PATH,
                                    'svn',
                                    self.test_env.CONFIG.DETECTOR,
                                    self.test_env.CONFIG.FILE_DETECTOR_RESULT)

        self.uut = result_evaluation.ResultEvaluation(self.test_env.CONFIG.DATA_PATH,
                                                      self.test_env.CONFIG.RESULTS_PATH,
                                                      self.test_env.CONFIG.DETECTOR,
                                                      self.test_env.CONFIG.FILE_DETECTOR_RESULT,
                                                      self.test_env.CONFIG.CHECKOUT_DIR,
                                                      catch_errors=False)

    def tearDown(self):
        self.test_env.tearDown()

    def test_correct_total(self):
        create_result(self.file_result_git, '')
        create_result(self.file_result_svn, 'File: some-class.java')
        actual_results = self.uut.evaluate_results()
        self.assertEquals(3, actual_results[0])

    def test_correct_applied(self):
        create_result(self.file_result_git, '')
        create_result(self.file_result_svn, 'File: some-class.java')
        actual_results = self.uut.evaluate_results()
        self.assertEquals(2, actual_results[1])

    def test_correct_found(self):
        create_result(self.file_result_git, '')
        create_result(self.file_result_svn, 'File: some-class.java')
        actual_results = self.uut.evaluate_results()
        self.assertEquals(1, actual_results[2])

    def test_uses_digraph(self):
        create_result(self.file_result_git,
                      'File: some-class.java' + os.linesep + '---' + os.linesep + 'digraph name {' + os.linesep +
                      '1 [label="{}"]'.format(self.test_env.git_misuse_label) +
                      os.linesep + '}')
        actual_results = self.uut.evaluate_results()
        self.assertEquals(1, actual_results[2])


def create_result(file_result, content):
    safe_write(content, file_result, append=False)


if __name__ == '__main__':
    unittest.main()
