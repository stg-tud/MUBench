#!/usr/bin/env python3
import logging
import logging.handlers
import sys
from datetime import datetime
from os import listdir, makedirs
from os.path import join, realpath, isdir, exists

from benchmark.data.experiment import Experiment
from benchmark.subprocesses.requirements import check_all_requirements
from benchmark.subprocesses.result_processing.visualize_results import Visualizer
from benchmark.subprocesses.tasking import TaskRunner
from benchmark.subprocesses.tasks.implementations import stats
from benchmark.subprocesses.tasks.implementations.checkout import Checkout
from benchmark.subprocesses.tasks.implementations.compile import Compile
from benchmark.subprocesses.tasks.implementations.detect import Detect
from benchmark.subprocesses.tasks.implementations.info import Info
from benchmark.subprocesses.tasks.implementations.review_check import ReviewCheck, ReviewCheckEx3
from benchmark.subprocesses.tasks.implementations.review_prepare import PrepareReviewOfBenchmarkWithPatternsTask, \
    PrepareReviewOfBenchmarkTask, \
    PrepareReviewOfTopFindingsTask
from benchmark.utils import command_line_util


class Benchmark:
    DATA_PATH = realpath("data")
    CHECKOUTS_PATH = realpath("checkouts")
    COMPILES_PATH = CHECKOUTS_PATH
    DETECTORS_PATH = realpath("detectors")
    FINDINGS_PATH = realpath("findings")
    REVIEW_PATH = realpath("reviews")

    EX1_SUBFOLDER = "detect-only"
    EX2_SUBFOLDER = "mine-and-detect"
    EX3_SUBFOLDER = "mine-and-detect"

    def __init__(self, config):
        self.reviewed_eval_result_file = 'reviewed-result.csv'
        self.visualize_result_file = 'result.csv'

        self.config = config

        if 'white_list' not in config:
            config.white_list = []
        if 'black_list' not in config:
            config.black_list = []
        self.runner = TaskRunner(Benchmark.DATA_PATH, config.white_list, config.black_list)

    def _run_visualize(self) -> None:
        visualizer = Visualizer(Benchmark.FINDINGS_PATH, self.reviewed_eval_result_file, self.visualize_result_file,
                                Benchmark.DATA_PATH)
        visualizer.create()

    def _setup_stats(self) -> None:
        stats_calculator = stats.get_calculator(self.config.script)
        self.runner.add(stats_calculator)

    def _setup_info(self):
        self.runner.add(Info(Benchmark.CHECKOUTS_PATH, Benchmark.COMPILES_PATH))

    def _setup_checkout(self):
        checkout_handler = Checkout(Benchmark.CHECKOUTS_PATH, self.config.force_checkout)
        self.runner.add(checkout_handler)

    def _setup_compile(self):
        compile_handler = Compile(Benchmark.CHECKOUTS_PATH, Benchmark.COMPILES_PATH, self.config.force_compile)
        self.runner.add(compile_handler)

    def _setup_detect(self):
        experiment = self.__get_experiment(self.config.detector)
        self.runner.add(Detect(Benchmark.COMPILES_PATH, experiment, self.config.timeout, self.config.force_detect))

    def _setup_review_prepare(self):
        detectors = available_detectors
        if self.config.detector_white_list:
            detectors = set(detectors).intersection(self.config.detector_white_list)

        for detector in detectors:
            experiment = self.__get_experiment(detector)
            if experiment.id == Experiment.PROVIDED_PATTERNS:
                self.runner.add(PrepareReviewOfBenchmarkWithPatternsTask(experiment, Benchmark.CHECKOUTS_PATH,
                                                                         Benchmark.COMPILES_PATH,
                                                                         self.config.force_prepare))
            elif experiment.id == Experiment.TOP_FINDINGS:
                self.runner.add(PrepareReviewOfTopFindingsTask(experiment, Benchmark.CHECKOUTS_PATH,
                                                               Benchmark.COMPILES_PATH, self.config.top_n_findings,
                                                               self.config.force_prepare))
            elif experiment.id == Experiment.BENCHMARK:
                self.runner.add(PrepareReviewOfBenchmarkTask(experiment, Benchmark.CHECKOUTS_PATH,
                                                             Benchmark.COMPILES_PATH, self.config.force_prepare))

    def __get_experiment(self, detector: str):
        ex_ids = {
            1: Experiment.PROVIDED_PATTERNS,
            2: Experiment.TOP_FINDINGS,
            3: Experiment.BENCHMARK
        }
        return Experiment(ex_ids.get(self.config.experiment), self.__get_detector(detector),
                          Benchmark.FINDINGS_PATH, Benchmark.REVIEW_PATH)

    def __get_detector(self, detector: str):
        from detectors.dummy.dummy import DummyDetector
        from detectors.dmmc.dmmc import Dmmc
        from detectors.grouminer.grouminer import Grouminer
        from detectors.jadet.jadet import Jadet
        from detectors.tikanga.tikanga import Tikanga
        from detectors.mudetect.mudetect import MuDetect
        detectors = {
            "dmmc": Dmmc,
            "grouminer": Grouminer,
            "jadet": Jadet,
            "tikanga": Tikanga,
            "mudetect": MuDetect,
        }
        java_options = ['-' + option for option in self.config.java_options]
        return detectors[detector](self.DETECTORS_PATH, detector, java_options) \
            if detector in detectors else DummyDetector(self.DETECTORS_PATH)

    def _setup_review_check(self):
        # TODO remove as soon as review server is in use
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
