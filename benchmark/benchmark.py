#!/usr/bin/env python3
import logging
import logging.handlers
import sys
from datetime import datetime
from os import listdir, makedirs
from os.path import join, realpath, isdir, exists

from benchmark.subprocesses.check import check_prerequisites
from benchmark.subprocesses.result_processing.visualize_results import Visualizer
from benchmark.subprocesses.tasking import TaskRunner
from benchmark.subprocesses.tasks.implementations import stats
from benchmark.subprocesses.tasks.implementations.checkout import Checkout
from benchmark.subprocesses.tasks.implementations.compile import Compile
from benchmark.subprocesses.tasks.implementations.detect import Detect
from benchmark.subprocesses.tasks.implementations.evaluate import Evaluate
from benchmark.utils import command_line_util


class Benchmark:
    DATA_PATH = realpath("data")
    CHECKOUTS_PATH = realpath("checkouts")
    RESULTS_PATH = realpath("results")

    def __init__(self, config):
        self.detector_result_file = 'findings.yml'
        self.eval_result_file = 'result.csv'
        self.reviewed_eval_result_file = 'reviewed-result.csv'
        self.visualize_result_file = 'result.csv'

        self.config = config

        if 'white_list' not in config:
            config.white_list = []
        if 'black_list' not in config:
            config.black_list = []
        self.runner = TaskRunner(Benchmark.DATA_PATH, config.white_list, config.black_list)

    def _run_visualize(self) -> None:
        visualizer = Visualizer(Benchmark.RESULTS_PATH, self.reviewed_eval_result_file, self.visualize_result_file,
                                Benchmark.DATA_PATH)
        visualizer.create()

    def _setup_stats(self) -> None:
        stats_calculator = stats.get_calculator(self.config.script)
        self.runner.add(stats_calculator)

    def _setup_checkout(self):
        checkout_handler = Checkout(Benchmark.CHECKOUTS_PATH, self.config.force_checkout)
        self.runner.add(checkout_handler)

    def _setup_compile(self):
        compile_handler = Compile(Benchmark.CHECKOUTS_PATH, Benchmark.CHECKOUTS_PATH, self.config.pattern_frequency,
                                  self.config.force_compile)
        self.runner.add(compile_handler)

    def _setup_detect(self):
        results_path = join(Benchmark.RESULTS_PATH, self.config.detector)
        detector_runner = Detect(self.config.detector, self.detector_result_file, Benchmark.CHECKOUTS_PATH,
                                 results_path,
                                 self.config.timeout, self.config.java_options, self.config.force_detect)
        self.runner.add(detector_runner)

    def _setup_eval(self):
        results_path = join(Benchmark.RESULTS_PATH, self.config.detector)
        evaluation_handler = Evaluate(results_path, Benchmark.CHECKOUTS_PATH,
                                      self.eval_result_file)
        self.runner.add(evaluation_handler)

    def run(self) -> None:
        check_prerequisites()
        if config.subprocess == 'visualize':
            self._run_visualize()
            return
        elif config.subprocess == 'check':
            pass
        elif config.subprocess == 'checkout':
            self._setup_checkout()
        elif config.subprocess == 'compile':
            self._setup_checkout()
            self._setup_compile()
        elif config.subprocess == 'detect':
            self._setup_checkout()
            self._setup_compile()
            self._setup_detect()
        elif config.subprocess == 'eval':
            self._setup_checkout()
            self._setup_compile()
            self._setup_detect()
            self._setup_eval()
        elif config.subprocess == 'stats':
            self._setup_stats()

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
available_scripts = stats.get_available_calculator_names()
config = command_line_util.parse_args(sys.argv, available_detectors, available_scripts)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(IndentFormatter("%(indent)s%(message)s"))
handler.setLevel(logging.INFO)
logger.addHandler(handler)
LOG_DIR = "logs"
if not exists(LOG_DIR):
    makedirs(LOG_DIR)
log_name = datetime.now().strftime("run_%Y%m%d_%H%M%S") + ".log"
handler = logging.FileHandler(join(LOG_DIR, log_name))
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info("Starting benchmark...")
logger.debug("- Arguments           = %r", sys.argv)
logger.debug("- Available Detectors = %r", available_detectors)
logger.debug("- Configuration       :")
for key in config.__dict__:
    logger.debug("    - %s = %r", key.ljust(15), config.__dict__[key])

benchmark = Benchmark(config)
benchmark.run()
