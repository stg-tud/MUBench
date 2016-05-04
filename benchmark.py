import sys
from configparser import ConfigParser
from os import getcwd, chdir, listdir
from os.path import join, realpath, dirname, pardir

from typing import Optional, List

from benchmark.checkout import Checkout
from benchmark.detector_runner import DetectorRunner
from benchmark.result_evaluation import ResultEvaluation
from benchmark.utils import command_line_util
from benchmark.utils.prerequisites_checker import check_prerequisites


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
        self.results_path = realpath(join("results", self.detector))
        self.checkout_dir = realpath("checkouts")

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

    def detect(self):
        detector_runner = DetectorRunner(self.data_path,
                                         self.detector,
                                         self.checkout_dir,
                                         self.results_path,
                                         self.timeout,
                                         self.white_list,
                                         self.black_list)

        detector_runner.run_detector_on_all_data()

    def evaluate(self):
        cfg = ConfigParser()
        cfg.read(realpath(join('detectors', self.detector, self.detector + '.cfg')))
        detector_result_file = cfg['DEFAULT']['Result File']
        result_evaluation = ResultEvaluation(self.data_path,
                                             self.results_path,
                                             self.detector,
                                             detector_result_file,
                                             self.checkout_dir)
        result_evaluation.evaluate_results()


mubench = dirname(__file__)
chdir(mubench)  # set the cwd to the MUBench folder
available_detectors = listdir(realpath('detectors'))
config = command_line_util.parse_args(sys.argv, available_detectors)

if config.subprocess == 'check':
    benchmark = MUBenchmark(detector="", white_list=[], black_list=[], timeout=None)
    # prerequisites are always checked implicitly
if config.subprocess == 'checkout':
    benchmark = MUBenchmark(detector="", white_list=[], black_list=[], timeout=None)
    benchmark.checkout()
if config.subprocess == 'detect':
    benchmark = MUBenchmark(detector=config.detector, white_list=config.white_list, black_list=config.black_list,
                            timeout=config.timeout)
    benchmark.detect()
if config.subprocess == 'eval':
    benchmark = MUBenchmark(detector=config.detector, white_list=[], black_list=[], timeout=None)
    benchmark.evaluate()
