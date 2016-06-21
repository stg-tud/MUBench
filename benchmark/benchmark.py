#!/usr/bin/env python3
import logging
import sys
from os import getcwd, listdir
from os.path import join, realpath, exists
from shutil import rmtree

from typing import Optional, List

from benchmark.subprocesses.check import Check
from benchmark.subprocesses.checkout import Checkout
from benchmark.subprocesses.compile import Compile
from benchmark.subprocesses.datareader import DataReader
from benchmark.subprocesses.detect import Detect
from benchmark.subprocesses.evaluate import Evaluation
from benchmark.subprocesses.visualize_results import Visualizer
from benchmark.utils import command_line_util


class MUBenchmark:
    def __init__(self,
                 detector: str,
                 timeout: Optional[int],
                 black_list: List[str],
                 white_list: List[str],
                 java_options: List[str],
                 force_detect: bool,
                 skip_compile: bool,
                 ):
        self.detector = detector
        self.timeout = timeout
        self.black_list = black_list
        self.white_list = white_list
        self.java_options = java_options
        self.force_detect = force_detect
        self.skip_compile = skip_compile
        self.data_path = join(getcwd(), "data")
        self.results_path = realpath(join("results", self.detector))
        self.checkout_dir = realpath("checkouts")
        self.checkout_subdir = "checkout"
        self.original_src = "original-src"
        self.original_classes = "original-classes"
        self.patterns_src = "patterns-src"
        self.patterns_classes = "patterns-classes"
        self.detector_result_file = 'findings.yml'
        self.eval_result_file = 'result.csv'
        self.reviewed_eval_result_file = 'reviewed-result.csv'
        self.visualize_result_file = 'result.csv'

        self.pattern_frequency = 20

        self.datareader = DataReader(self.data_path, self.white_list, self.black_list)

        self.datareader.add(Check())

    def run_check(self):
        # check subprocess is always registered by __init__
        self.datareader.black_list = [""]
        self.run()

    def run_checkout(self) -> None:
        self._setup_checkout(setup_revisions=False, checkout_parent=False)
        self.run()

    def run_compile(self) -> None:
        self._setup_checkout(setup_revisions=True, checkout_parent=True)
        self._setup_compile()
        self.run()

    def run_detect(self) -> None:
        self._setup_checkout(setup_revisions=True, checkout_parent=True)
        self._setup_compile()
        self._setup_detect()
        self.run()

    def run_evaluate(self) -> None:
        if self.force_detect or not exists(self.results_path):
            if exists(self.results_path):
                def print_error_and_exit(func, path, _):
                    exit("Couldn't delete directory `{}`! ".format(path) +
                         "Please make sure no other applications are using it or delete it manually.")

                rmtree(self.results_path, onerror=print_error_and_exit)

            self._setup_checkout(setup_revisions=True, checkout_parent=True)
            self._setup_compile()
            self._setup_detect()

        self._setup_eval()

        self.run()

    def run_visualize(self) -> None:
        visualizer = Visualizer(realpath("results"), self.reviewed_eval_result_file, self.visualize_result_file)
        visualizer.run()

    def _setup_checkout(self, setup_revisions: bool, checkout_parent: bool):
        checkout_handler = Checkout(checkout_parent, setup_revisions, self.checkout_subdir)
        self.datareader.add(checkout_handler)

    def _setup_compile(self):
        if not self.skip_compile:
            compile_handler = Compile(self.checkout_dir, self.checkout_subdir,
                                      self.original_src, self.original_classes,
                                      self.patterns_src, self.patterns_classes, self.pattern_frequency,
                                      "compile-out.log", "compile-error.log")
            self.datareader.add(compile_handler)

    def _setup_detect(self):
        detector_runner = Detect(self.detector, self.detector_result_file, self.checkout_dir, self.original_src,
                                 self.original_classes, self.patterns_src, self.patterns_classes, self.results_path,
                                 self.timeout, self.java_options)
        self.datareader.add(detector_runner)

    def _setup_eval(self):
        evaluation_handler = Evaluation(self.results_path, self.detector_result_file, self.checkout_dir,
                                        self.eval_result_file)
        self.datareader.add(evaluation_handler)

    def run(self) -> None:
        self.datareader.run()


class IndentFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, rec):
        logger_name = rec.name
        logger_level = 0
        if logger_name:
            logger_level = logger_name.count('.') + 1
        rec.indent = "    " * logger_level
        out = logging.Formatter.format(self, rec)
        out = out.replace("\n", "\n" + rec.indent)
        del rec.indent
        return out

formatter = IndentFormatter("%(indent)s%(message)s")

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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
if 'skip_compile' not in config:
    config.skip_compile = False

benchmark = MUBenchmark(detector=config.detector, white_list=config.white_list, black_list=config.black_list,
                        timeout=config.timeout, java_options=config.java_options, force_detect=config.force_detect,
                        skip_compile=config.skip_compile)

if config.subprocess == 'check':
    benchmark.run_check()
if config.subprocess == 'checkout':
    benchmark.run_checkout()
if config.subprocess == 'compile':
    benchmark.run_compile()
if config.subprocess == 'detect':
    benchmark.run_detect()
if config.subprocess == 'eval':
    benchmark.run_evaluate()
if config.subprocess == 'visualize':
    benchmark.run_visualize()
