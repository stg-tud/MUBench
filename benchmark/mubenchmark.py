import sys
from datetime import datetime
from os import getcwd, chdir
from os.path import join, realpath, dirname, pardir

from typing import Optional, List

from checkout import Checkout
from detector_runner import DetectorRunner
from result_evaluation import ResultEvaluation
from utils.prerequisites_checker import check_prerequisites


class MUBenchmark:
    def __init__(self,
                 detector: str,
                 timeout: Optional[int] = None,
                 black_list: List[str] = [],
                 white_list: List[str] = [""]
                 ):
        mubench = join(dirname(__file__), pardir)
        chdir(mubench)  # set the cwd to the MUBench folder

        self.detector = detector
        self.timeout = timeout
        self.black_list = black_list
        self.white_list = white_list

        self.data_path = join(getcwd(), "data")
        self.detector_result_file = "result.txt"
        self.results_path = realpath(join(pardir, "MUBenchmark-results", self.detector))
        self.checkout_dir = realpath(join(pardir, "MUBenchmark-checkouts"))

    @staticmethod
    def check():
        prerequisites_okay, error_message = check_prerequisites()
        if not prerequisites_okay:
            print('')  # add the before omitted newline
            sys.exit(error_message)

    def checkout(self):
        checkout = Checkout(self.data_path, self.checkout_dir)
        checkout.do_all_checkouts()

    def mine(self):
        pass  # TODO implement a miner_runner

    def evaluate(self):
        start_time = datetime.now()
        try:
            detector_runner = DetectorRunner(self.data_path,
                                             self.detector,
                                             self.checkout_dir,
                                             self.results_path,
                                             self.timeout)

            detector_runner.run_detector_on_all_data()

        except (KeyboardInterrupt, SystemExit):
            end_time = datetime.now()
            print("================================================")
            print("Analysis cancelled! Total time: {}".format(str(end_time - start_time)))
            print("================================================")
        else:
            end_time = datetime.now()
            print("================================================")
            print("Analysis finished! Total time: {}".format(str(end_time - start_time)))
            print("================================================")

        finally:
            print("Evaluating results...")
            result_evaluation = ResultEvaluation(self.data_path,
                                                 self.results_path,
                                                 self.detector,
                                                 self.detector_result_file,
                                                 self.checkout_dir)
            result_evaluation.evaluate_results()
            end_time = datetime.now()
            print("Total evaluation time: {}".format(str(end_time - start_time)))

benchmark = MUBenchmark(detector='dummy-miner')
benchmark.check()
benchmark.checkout()
benchmark.mine()
benchmark.evaluate()

print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("++++++++++++++++++++++++ FINISHED +++++++++++++++++++++++++")
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
