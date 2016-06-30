#!/usr/bin/env python3
import logging
import logging.handlers
import sys
from os import listdir
from os.path import join, realpath, isdir, exists
from typing import Optional, List

from benchmark.subprocesses.check import check_prerequisites
from benchmark.subprocesses.result_processing.visualize_results import Visualizer
from benchmark.subprocesses.tasking import TaskRunner
from benchmark.subprocesses.tasks.implementations.checkout import Checkout
from benchmark.subprocesses.tasks.implementations.compile import Compile
from benchmark.subprocesses.tasks.implementations.detect import Detect
from benchmark.subprocesses.tasks.implementations.evaluate import Evaluate
from benchmark.utils import command_line_util

LOG_FILE_NAME = "out.log"


class Benchmark:
    DATA_PATH = realpath("data")
    CHECKOUTS_PATH = realpath("checkouts")
    RESULTS_PATH = realpath("results")

    def __init__(self,
                 detector: str,
                 timeout: Optional[int],
                 black_list: List[str],
                 white_list: List[str],
                 java_options: List[str],
                 force_detect: bool,
                 force_checkout: bool,
                 force_compile: bool
                 ):
        # command-line options
        self.detector = detector
        self.timeout = timeout
        self.black_list = black_list
        self.white_list = white_list
        self.java_options = java_options
        self.force_checkout = force_checkout
        self.force_detect = force_detect
        self.force_compile = force_compile
        self.pattern_frequency = 20  # TODO make configurable

        self.results_path = join(Benchmark.RESULTS_PATH, self.detector)

        self.detector_result_file = 'findings.yml'
        self.eval_result_file = 'result.csv'
        self.reviewed_eval_result_file = 'reviewed-result.csv'
        self.visualize_result_file = 'result.csv'

        self.runner = TaskRunner(Benchmark.DATA_PATH, self.white_list, self.black_list)

    def run_checkout(self) -> None:
        self._setup_checkout()
        self.run()

    def run_compile(self) -> None:
        self._setup_checkout()
        self._setup_compile()
        self.run()

    def run_detect(self) -> None:
        self._setup_checkout()
        self._setup_compile()
        self._setup_detect()
        self.run()

    def run_evaluate(self) -> None:
        self._setup_checkout()
        self._setup_compile()
        self._setup_detect()
        self._setup_eval()
        self.run()

    def run_visualize(self) -> None:
        visualizer = Visualizer(Benchmark.RESULTS_PATH, self.reviewed_eval_result_file, self.visualize_result_file,
                                Benchmark.DATA_PATH)
        visualizer.create()

    def _setup_checkout(self):
        checkout_handler = Checkout(Benchmark.CHECKOUTS_PATH, self.force_checkout)
        self.runner.add(checkout_handler)

    def _setup_compile(self):
        compile_handler = Compile(Benchmark.CHECKOUTS_PATH, Benchmark.CHECKOUTS_PATH, self.pattern_frequency,
                                  self.force_compile)
        self.runner.add(compile_handler)

    def _setup_detect(self):
        detector_runner = Detect(self.detector, self.detector_result_file, Benchmark.CHECKOUTS_PATH, self.results_path,
                                 self.timeout, self.java_options, self.force_detect)
        self.runner.add(detector_runner)

    def _setup_eval(self):
        evaluation_handler = Evaluate(self.results_path, self.detector_result_file, Benchmark.CHECKOUTS_PATH,
                                      self.eval_result_file)
        self.runner.add(evaluation_handler)

    def run(self) -> None:
        self.runner.run()


class IndentFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, rec):
        logger_name = rec.name
        logger_level = 0
        if logger_name != "root":
            logger_level = logger_name.count('.') + 1
        rec.indent = "    " * logger_level
        out = logging.Formatter.format(self, rec)
        out = out.replace("\n", "\n" + rec.indent)
        del rec.indent
        return out


detectors_path = realpath('detectors')
available_detectors = [detector for detector in listdir(detectors_path) if isdir(join(detectors_path, detector))]
config = command_line_util.parse_args(sys.argv, available_detectors)

if 'detector' not in config:
    config.detector = ''
if 'white_list' not in config:
    config.white_list = []
if 'black_list' not in config:
    config.black_list = []
if 'timeout' not in config:
    config.timeout = None
if 'java_options' not in config:
    config.java_options = []
if 'force_detect' not in config:
    config.force_detect = False
if 'force_checkout' not in config:
    config.force_checkout = False
if 'force_compile' not in config:
    config.force_compile = False


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(IndentFormatter("%(indent)s%(message)s"))
handler.setLevel(logging.INFO)
logger.addHandler(handler)
needs_new_logfile = exists(LOG_FILE_NAME)
handler = logging.handlers.RotatingFileHandler(LOG_FILE_NAME, backupCount=50)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
if needs_new_logfile:
    handler.doRollover()

logger.info("Starting benchmark...")
logger.debug("- Arguments           = %r", sys.argv)
logger.debug("- Available Detectors = %r", available_detectors)
logger.debug("- Configuration       :")
for key in config.__dict__:
    logger.debug("    - %s = %r", key.ljust(15), config.__dict__[key])

benchmark = Benchmark(detector=config.detector, white_list=config.white_list, black_list=config.black_list,
                      timeout=config.timeout, java_options=config.java_options, force_detect=config.force_detect,
                      force_checkout=config.force_checkout, force_compile=config.force_compile)

check_prerequisites()

if config.subprocess == 'check':
    pass
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
