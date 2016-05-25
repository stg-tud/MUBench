#!/usr/bin/env python3
import inspect
import sys
from configparser import ConfigParser
from os import getcwd, chdir, listdir
from os.path import join, realpath, dirname, exists

from shutil import rmtree
from typing import Optional, List

from benchmark.checkout import Checkout
from benchmark.datareader import DataReader
from benchmark.detect import Detect
from benchmark.evaluate import Evaluation
from benchmark.utils import command_line_util
from benchmark.utils.io import safe_open
from benchmark.utils.prerequisites_checker import check_prerequisites


class MUBenchmark:
    def __init__(self,
                 detector: str,
                 timeout: Optional[int],
                 black_list: List[str],
                 white_list: List[str],
                 java_options: List[str],
                 force_detect: bool
                 ):
        self.detector = detector
        self.timeout = timeout
        self.black_list = black_list
        self.white_list = white_list
        self.java_options = java_options
        self.force_detect = force_detect
        self.data_path = join(getcwd(), "data")
        self.results_path = realpath(join("results", self.detector))
        self.checkout_dir = realpath("checkouts")
        self.detector_result_file = 'findings.yml'

        self.datareader = DataReader(self.data_path, self.white_list, self.black_list)

    def checkout(self) -> None:
        checkout_handler = Checkout(setup_revisions=False, checkout_parent=False,
                                    outlog=safe_open(join('checkouts', 'stdout.log'), 'a+'),
                                    errlog=safe_open(join('checkouts', 'stderr.log'), 'a+'))
        self.datareader.add(checkout_handler.checkout)
        self.datareader.run()

    def detect(self) -> None:
        detector_runner = Detect(self.detector, self.detector_result_file, self.checkout_dir, self.results_path,
                                 self.timeout, self.java_options)
        checkout_handler = Checkout(setup_revisions=True, checkout_parent=True,
                                    outlog=safe_open(join('checkouts', 'stdout.log'), 'a+'),
                                    errlog=safe_open(join('checkouts', 'stderr.log'), 'a+'))

        self.datareader.add(checkout_handler.checkout)
        self.datareader.add(detector_runner.run_detector)
        self.datareader.run()

    def evaluate(self) -> None:
        evaluation_handler = Evaluation(self.results_path, self.detector_result_file, self.checkout_dir)

        if self.force_detect:
            rmtree(self.results_path)

        if not exists(self.results_path):
            detector_runner = Detect(self.detector, self.detector_result_file, self.checkout_dir,
                                     self.results_path, self.timeout, self.java_options)
            checkout_handler = Checkout(setup_revisions=True, checkout_parent=True,
                                        outlog=safe_open(join('checkouts', 'stdout.log'), 'a+'),
                                        errlog=safe_open(join('checkouts', 'stderr.log'), 'a+'))
            self.datareader.add(checkout_handler.checkout)
            self.datareader.add(detector_runner.run_detector)

        self.datareader.add(evaluation_handler.evaluate)

        self.datareader.run()

        evaluation_handler.output_results()


def check() -> None:
    print("Checking prerequisites... ", end='')
    prerequisites_okay, error_message = check_prerequisites()
    if not prerequisites_okay:
        print('')  # add the before omitted newline
        sys.exit(error_message)
    else:
        print("okay")


mubench = dirname(realpath(inspect.stack()[0][1]))  # most reliable way to get the scripts absolute location
chdir(mubench)  # set the cwd to the MUBench folder
available_detectors = listdir(realpath('detectors'))
config = command_line_util.parse_args(sys.argv, available_detectors)

check()

if 'detector' not in config:
    config.detector = ''
if 'white_list' not in config:
    config.white_list = [""]
if 'black_list' not in config:
    config.black_list = []
if 'timeout' not in config:
    config.timeout = None
if 'java_options' not in config:
    config.java_options = []
if 'force_detect' not in config:
    config.force_detect = False

benchmark = MUBenchmark(detector=config.detector, white_list=config.white_list, black_list=config.black_list,
                        timeout=config.timeout, java_options=config.java_options, force_detect=config.force_detect)

if config.subprocess == 'check':
    pass  # prerequisites are always checked before
if config.subprocess == 'checkout':
    benchmark.checkout()
if config.subprocess == 'detect':
    benchmark.detect()
if config.subprocess == 'eval':
    benchmark.evaluate()
