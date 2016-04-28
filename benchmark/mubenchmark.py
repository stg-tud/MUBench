import sys
from datetime import datetime

from checkout import Checkout
from config import Config
from detector_runner import DetectorRunner
from result_evaluation import ResultEvaluation
from utils.prerequisites_checker import check_prerequisites


class MUBenchmark:
    def __init__(self, config: Config):
        self.config = config

    @staticmethod
    def check():
        prerequisites_okay, error_message = check_prerequisites()
        if not prerequisites_okay:
            print('')  # add the before omitted newline
            sys.exit(error_message)

    def checkout(self):
        checkout = Checkout(self.config.DATA_PATH, self.config.CHECKOUT_DIR)
        checkout.do_all_checkouts()

    def mine(self):
        pass  # TODO implement a miner_runner

    def evaluate(self):
        start_time = datetime.now()
        try:
            detector_runner = DetectorRunner(self.config.DATA_PATH,
                                             self.config.DETECTOR,
                                             self.config.CHECKOUT_DIR,
                                             self.config.RESULTS_PATH,
                                             self.config.TIMEOUT)

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
            result_evaluation = ResultEvaluation(self.config.DATA_PATH,
                                                 self.config.RESULTS_PATH,
                                                 self.config.DETECTOR,
                                                 self.config.FILE_DETECTOR_RESULT,
                                                 self.config.CHECKOUT_DIR)
            result_evaluation.evaluate_results()
            end_time = datetime.now()
            print("Total evaluation time: {}".format(str(end_time - start_time)))


benchmark = MUBenchmark(Config())

benchmark.check()
benchmark.checkout()
benchmark.evaluate()

print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("++++++++++++++++++++++++ FINISHED +++++++++++++++++++++++++")
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
