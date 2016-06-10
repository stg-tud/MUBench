#!/usr/bin/env python3
import inspect
import sys
from os import getcwd, chdir, listdir
from os.path import join, realpath, dirname, exists
from shutil import rmtree

from typing import Optional, List

from benchmark.subprocesses.check import Check
from benchmark.subprocesses.checkout import Checkout
from benchmark.subprocesses.compile import Compile
from benchmark.subprocesses.datareader import DataReader
from benchmark.subprocesses.detect import Detect
from benchmark.subprocesses.evaluate import Evaluation
from benchmark.utils import command_line_util
from benchmark.utils.io import safe_open


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
        self.checkout_subdir = "checkout"
        self.original_src = "original-src"
        self.original_classes = "original-classes"
        self.patterns_src = "patterns-src"
        self.patterns_classes = "patterns-classes"
        self.detector_result_file = 'findings.yml'

        self.pattern_frequency = 20

        self.datareader = DataReader(self.data_path, self.white_list, self.black_list)

        self.datareader.add(Check())

    def run_check(self):
        # check subprocess is always registered by __init__
        self.datareader.black_list = [""]
        self.datareader.run()

    def run_checkout(self) -> None:
        self._setup_checkout(setup_revisions=False, checkout_parent=False)
        self.run()

    def run_detect(self) -> None:
        self._setup_detect()
        self.datareader.run()

    def run_evaluate(self) -> None:
        if self.force_detect or not exists(self.results_path):
            if exists(self.results_path):
                def print_error_and_exit(func, path, _):
                    exit("Couldn't delete directory `{}`! ".format(path) +
                         "Please make sure no other applications are using it or delete it manually.")

                rmtree(self.results_path, onerror=print_error_and_exit)

            self._setup_detect()

        self._setup_eval()

        self.datareader.run()

    def _setup_compile(self):
        compile_handler = Compile(self.checkout_dir, self.checkout_subdir,
                                  self.original_src, self.original_classes,
                                  self.patterns_src, self.patterns_classes, self.pattern_frequency,
                                  join(self.checkout_dir, "compile-out.log"),
                                  join(self.checkout_dir, "compile-error.log"))
        self.datareader.add(compile_handler)

    def _setup_checkout(self, setup_revisions: bool, checkout_parent: bool):
        checkout_handler = Checkout(setup_revisions=setup_revisions, checkout_parent=checkout_parent,
                                    checkout_subdir=self.checkout_subdir,
                                    outlog=safe_open(join('checkouts', 'checkout-out.log'), 'a+'),
                                    errlog=safe_open(join('checkouts', 'checkout-error.log'), 'a+'))
        self.datareader.add(checkout_handler)

    def _setup_detect(self):
        self._setup_checkout(setup_revisions=True, checkout_parent=True)
        self._setup_compile()
        detector_runner = Detect(self.detector, self.detector_result_file, self.checkout_dir, self.original_src,
                                 self.original_classes, self.patterns_src, self.patterns_classes, self.results_path,
                                 self.timeout, self.java_options)
        self.datareader.add(detector_runner)

    def _setup_eval(self):
        self.evaluation_handler = Evaluation(self.results_path, self.detector_result_file, self.checkout_dir)
        self.datareader.add(self.evaluation_handler)

    def run(self) -> None:
        self.datareader.run()


mubench = dirname(realpath(inspect.stack()[0][1]))  # most reliable way to get the scripts absolute location
chdir(mubench)  # set the cwd to the MUBench folder
available_detectors = listdir(realpath('detectors'))
config = command_line_util.parse_args(sys.argv, available_detectors)

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
    benchmark.run_check()
if config.subprocess == 'checkout':
    benchmark.run_checkout()
if config.subprocess == 'detect':
    benchmark.run_detect()
if config.subprocess == 'eval':
    benchmark.run_evaluate()
