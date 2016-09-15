#!/usr/bin/env python3
import logging
import logging.handlers
import sys
from datetime import datetime
from os import listdir, makedirs
from os.path import join, realpath, isdir, exists

from benchmark.subprocesses.requirements import check_all_requirements
from benchmark.subprocesses.result_processing.visualize_results import Visualizer
from benchmark.subprocesses.tasking import TaskRunner
from benchmark.subprocesses.tasks.implementations import stats
from benchmark.subprocesses.tasks.implementations.checkout import Checkout
from benchmark.subprocesses.tasks.implementations.compile import Compile
from benchmark.subprocesses.tasks.implementations.detect import Detect
from benchmark.subprocesses.tasks.implementations.info import Info
from benchmark.subprocesses.tasks.implementations.review_check import ReviewCheck, ReviewCheckEx3
from benchmark.subprocesses.tasks.implementations.review_prepare import ReviewPrepareEx1, ReviewPrepareEx2, \
    ReviewPrepareEx3
from benchmark.utils import command_line_util


class Benchmark:
    DATA_PATH = realpath("data")
    CHECKOUTS_PATH = realpath("checkouts")
    RESULTS_PATH = realpath("findings")
    REVIEW_PATH = realpath("reviews")

    EX1_SUBFOLDER = "ex1_detect-only"
    EX2_SUBFOLDER = "ex2_detect-only"
    EX3_SUBFOLDER = "ex3_detect-only"

    def __init__(self, config):
        self.detector_result_file = 'findings.yml'
        self.detector_run_info_file = 'run.yml'
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

    def _setup_info(self):
        self.runner.add(Info(Benchmark.CHECKOUTS_PATH, Benchmark.CHECKOUTS_PATH))

    def _setup_checkout(self):
        checkout_handler = Checkout(Benchmark.CHECKOUTS_PATH, self.config.force_checkout)
        self.runner.add(checkout_handler)

    def _setup_compile(self):
        compile_handler = Compile(Benchmark.CHECKOUTS_PATH, Benchmark.CHECKOUTS_PATH, self.config.force_compile)
        self.runner.add(compile_handler)

    def _setup_detect(self):
        results_path = Benchmark.RESULTS_PATH
        if config.experiment == 1:
            results_path = join(results_path, Benchmark.EX1_SUBFOLDER)
        elif config.experiment == 2:
            results_path = join(results_path, Benchmark.EX2_SUBFOLDER)
        elif config.experiment == 3:
            results_path = join(results_path, Benchmark.EX3_SUBFOLDER)

        # TODO make task append the detector name to the results path
        results_path = join(results_path, self.config.detector)

        self.runner.add(Detect(self.config.detector, self.detector_result_file, self.detector_run_info_file,
                               Benchmark.CHECKOUTS_PATH, results_path, self.config.experiment, self.config.timeout,
                               self.config.java_options, self.config.force_detect))

    def _setup_review_prepare(self):
        detectors = available_detectors
        if config.detector_white_list:
            detectors = set(detectors).intersection(config.detector_white_list)

        for detector in detectors:
            results_path = join(Benchmark.RESULTS_PATH, detector)
            if config.experiment == 1:
                self.runner.add(ReviewPrepareEx1(Benchmark.EX1_SUBFOLDER, detector, results_path, Benchmark.REVIEW_PATH,
                                                 Benchmark.CHECKOUTS_PATH, Benchmark.CHECKOUTS_PATH,
                                                 self.config.force_prepare))
            elif config.experiment == 2:
                self.runner.add(ReviewPrepareEx2(Benchmark.EX2_SUBFOLDER, detector, results_path, Benchmark.REVIEW_PATH,
                                                 Benchmark.CHECKOUTS_PATH, Benchmark.CHECKOUTS_PATH,
                                                 self.config.force_prepare))
            elif config.experiment == 3:
                self.runner.add(ReviewPrepareEx3(Benchmark.EX3_SUBFOLDER, detector, results_path, Benchmark.REVIEW_PATH,
                                                 Benchmark.CHECKOUTS_PATH, Benchmark.CHECKOUTS_PATH,
                                                 self.config.top_n_findings, self.config.force_prepare))

    def _setup_review_check(self):
        if not exists(Benchmark.REVIEW_PATH):
            return

        if config.experiment == 1:
            self.runner.add(ReviewCheck(Benchmark.EX1_SUBFOLDER, Benchmark.REVIEW_PATH, available_detectors))
        elif config.experiment == 2:
            self.runner.add(ReviewCheck(Benchmark.EX2_SUBFOLDER, Benchmark.REVIEW_PATH, available_detectors))
        elif config.experiment == 3:
            self.runner.add(ReviewCheckEx3(Benchmark.EX3_SUBFOLDER, Benchmark.REVIEW_PATH, available_detectors))

    def run(self) -> None:
        if config.subprocess == 'visualize':
            self._run_visualize()
            return
        elif config.subprocess == 'check':
            check_all_requirements()
            return
        elif config.subprocess == 'info':
            self._setup_info()
        elif config.subprocess == 'checkout':
            self._setup_checkout()
        elif config.subprocess == 'compile':
            self._setup_checkout()
            self._setup_compile()
        elif config.subprocess == 'detect':
            self._setup_checkout()
            self._setup_compile()
            self._setup_detect()
        elif config.subprocess == 'review:prepare':
            self._setup_review_prepare()
        elif config.subprocess == 'review:check':
            self._setup_review_check()
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
