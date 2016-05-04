import sys
from configparser import ConfigParser
from datetime import datetime
from os import getcwd, chdir, listdir
from os.path import join, realpath, dirname, pardir

from typing import Optional, List

from checkout import Checkout
from detector_runner import DetectorRunner
from result_evaluation import ResultEvaluation
from utils.prerequisites_checker import check_prerequisites
from utils import command_line_util


class MUBenchmark:
    def __init__(self,
                 detector: str,
                 timeout: Optional[int],
                 black_list: List[str],
                 white_list: List[str]
                 ):

        self.detector = detector
        self.timeout = timeout
        self.black_list = black_list
        self.white_list = white_list
        self.data_path = join(getcwd(), "data")
        self.results_path = realpath(join("MUBenchmark-results", self.detector))
        self.checkout_dir = realpath("MUBenchmark-checkouts")

        self.check()

    @staticmethod
    def check():
        print("Checking prerequisites... ", end='')
        prerequisites_okay, error_message = check_prerequisites()
        if not prerequisites_okay:
            print('')  # add the before omitted newline
            sys.exit(error_message)
        else:
            print("okay")

    def checkout(self):
        checkout = Checkout(self.data_path, self.checkout_dir)
        checkout.do_all_checkouts()

    def mine(self):
        print("'mine' subprocess is not yet implemented.")  # TODO implement a miner_runner

    def evaluate(self):
        start_time = datetime.now()

        try:
            detector_runner = DetectorRunner(self.data_path,
                                             self.detector,
                                             self.checkout_dir,
                                             self.results_path,
                                             self.timeout,
                                             self.white_list,
                                             self.black_list)

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

        cfg = ConfigParser()
        cfg.read(realpath(join('detectors', self.detector, self.detector + '.cfg')))
        detector_result_file = cfg['DEFAULT']['Result File']

        print("Evaluating results...")
        result_evaluation = ResultEvaluation(self.data_path,
                                             self.results_path,
                                             self.detector,
                                             detector_result_file,
                                             self.checkout_dir,
                                             self.white_list,
                                             self.black_list)
        result_evaluation.evaluate_results()
        end_time = datetime.now()
        print("Total evaluation time: {}".format(str(end_time - start_time)))

mubench = join(dirname(__file__), pardir)
chdir(mubench)  # set the cwd to the MUBench folder
available_detectors = listdir(realpath('detectors'))
config = command_line_util.parse_args(sys.argv, available_detectors)

if config.mode == 'check':
    benchmark = MUBenchmark(detector="", white_list=[], black_list=[], timeout=None)
    # prerequisites are always checked implicitly
    sys.exit()
if config.mode == 'checkout':
    benchmark = MUBenchmark(detector="", white_list=[""], black_list=[], timeout=None)
    benchmark.checkout()
if config.mode == 'mine':
    benchmark = MUBenchmark(detector="", white_list=config.white_list, black_list=config.black_list,
                            timeout=config.timeout)
    benchmark.mine()
if config.mode == 'eval':
    benchmark = MUBenchmark(detector=config.detector, white_list=config.white_list, black_list=config.black_list,
                            timeout=config.timeout)
    benchmark.evaluate()
