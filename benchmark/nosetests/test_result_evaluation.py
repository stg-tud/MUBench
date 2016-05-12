from os.path import join

from benchmark.nosetests.test_utils.test_env_util import TestEnv
from benchmark.result_evaluation import ResultEvaluation
from benchmark.utils.io import safe_write


# noinspection PyAttributeOutsideInit
class TestResultEvaluation:
    def setup(self):
        self.test_env = TestEnv()

        self.file_result_git = join(self.test_env.RESULTS_PATH, self.test_env.DETECTOR, 'git',
                                    self.test_env.FILE_DETECTOR_RESULT)
        self.file_result_svn = join(self.test_env.RESULTS_PATH, self.test_env.DETECTOR, 'svn',
                                    self.test_env.FILE_DETECTOR_RESULT)

        self.uut = ResultEvaluation(self.test_env.RESULTS_PATH, self.test_env.DETECTOR,
                                    self.test_env.FILE_DETECTOR_RESULT, self.test_env.CHECKOUT_DIR)

    def teardown(self):
        self.test_env.tearDown()

        # TODO implement unittests for checkouts


def create_result(file_result, content):
    safe_write(content, file_result, append=False)
