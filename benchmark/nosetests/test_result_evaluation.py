import os
from os.path import join
from unittest import SkipTest

from nose.tools import assert_equals

from benchmark.nosetests.test_utils.test_env_util import TestEnv
from benchmark.result_evaluation import ResultEvaluation
from benchmark.utils.io import safe_write


# noinspection PyAttributeOutsideInit
class TestResultEvaluation:
    def setup(self):
        self.test_env = TestEnv()

        self.file_result_git = join(self.test_env.RESULTS_PATH,
                                    self.test_env.DETECTOR,
                                    'git',
                                    self.test_env.FILE_DETECTOR_RESULT)
        self.file_result_svn = join(self.test_env.RESULTS_PATH,
                                    self.test_env.DETECTOR,
                                    'svn',
                                    self.test_env.FILE_DETECTOR_RESULT)

        self.uut = ResultEvaluation(self.test_env.RESULTS_PATH,
                                    self.test_env.DETECTOR,
                                    self.test_env.FILE_DETECTOR_RESULT,
                                    self.test_env.CHECKOUT_DIR,
                                    catch_errors=False)

    def teardown(self):
        self.test_env.tearDown()

    @SkipTest
    def test_correct_total(self):
        create_result(self.file_result_git, '')
        create_result(self.file_result_svn, 'File: some-class.java')
        actual_results = self.uut.evaluate_results()
        assert_equals(3, actual_results[0])

    @SkipTest
    def test_correct_applied(self):
        create_result(self.file_result_git, '')
        create_result(self.file_result_svn, 'File: some-class.java')
        actual_results = self.uut.evaluate_results()
        assert_equals(2, actual_results[1])

    @SkipTest
    def test_correct_found(self):
        create_result(self.file_result_git, '')
        create_result(self.file_result_svn, 'File: some-class.java')
        actual_results = self.uut.evaluate_results()
        assert_equals(1, actual_results[2])

    @SkipTest
    def test_uses_digraph(self):
        create_result(self.file_result_git,
                      'File: some-class.java' + os.linesep + '---' + os.linesep + 'digraph name {' + os.linesep +
                      '1 [label="{}"]'.format(self.test_env.git_misuse_label) +
                      os.linesep + '}')
        actual_results = self.uut.evaluate_results()
        assert_equals(1, actual_results[2])


def create_result(file_result, content):
    safe_write(content, file_result, append=False)
