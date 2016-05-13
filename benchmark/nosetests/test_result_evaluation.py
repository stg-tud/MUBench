from os import chdir
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from benchmark.evaluate import Evaluation
from benchmark.utils.io import safe_write


# noinspection PyAttributeOutsideInit
class TestResultEvaluation:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-datareader-test_')

        chdir(self.temp_dir)

        self.checkout_dir = join(self.temp_dir, 'checkouts')
        self.results_path = join(self.temp_dir, 'results')
        self.detector = 'dummy-detector'
        self.file_detector_result = 'findings.yaml'

        self.uut = Evaluation(self.results_path, self.detector,
                              self.file_detector_result, self.checkout_dir)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_result_evaluation(self):
        pass  # TODO implement unittests

    def create_result(self, misuse_name, content):
        safe_write(content, join(self.results_path, self.detector, misuse_name, self.file_detector_result),
                   append=False)
