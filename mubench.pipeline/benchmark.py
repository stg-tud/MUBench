#!/usr/bin/env python3

import logging.handlers
import os
import sys
from datetime import datetime
from os import makedirs
from os.path import join, exists, abspath, dirname

from data.detectors import find_detector, get_available_detector_ids
from data.experiments import ProvidedPatternsExperiment, TopFindingsExperiment, BenchmarkExperiment
from task_runner import TaskRunner
from tasks.implementations import stats
from tasks.implementations.dataset_check import DatasetCheck
from tasks.implementations.requirements_check import RequirementsCheck
from tasks.implementations.checkout import Checkout
from tasks.implementations.compile import Compile
from tasks.implementations.detect import Detect
from tasks.implementations.info import Info
from tasks.implementations.publish_findings_task import PublishFindingsTask
from tasks.implementations.publish_metadata_task import PublishMetadataTask
from utils import command_line_util
from utils.dataset_util import get_datasets, get_available_dataset_ids, get_white_list
from utils.logging import IndentFormatter

MUBENCH_ROOT_PATH = join(dirname(abspath(__file__)), os.pardir)


class Benchmark:
    DATA_PATH = join(MUBENCH_ROOT_PATH, "data")
    CHECKOUTS_PATH = join(MUBENCH_ROOT_PATH, "checkouts")
    COMPILES_PATH = CHECKOUTS_PATH
    DETECTORS_PATH = join(MUBENCH_ROOT_PATH, "detectors")
    FINDINGS_PATH = join(MUBENCH_ROOT_PATH, "findings")
    DATASETS_FILE_PATH = join(DATA_PATH, 'datasets.yml')

    EX1_SUBFOLDER = "detect-only"
    EX2_SUBFOLDER = "mine-and-detect"
    EX3_SUBFOLDER = "mine-and-detect"

    def __init__(self, config):
        self.reviewed_eval_result_file = 'reviewed-result.csv'
        self.visualize_result_file = 'result.csv'

        self.config = config

        white_list = []
        black_list = []
        if 'white_list' in config:
            white_list.extend(config.white_list)
        if 'black_list' in config:
            black_list.extend(config.black_list)

        if 'dataset' in config:
            white_list.extend(get_white_list(self.DATASETS_FILE_PATH, config.dataset))

        self.runner = TaskRunner(Benchmark.DATA_PATH, white_list, black_list)

    def _setup_check(self):
        self.runner.add(RequirementsCheck())

    def _setup_dataset_check(self):
        self.runner.add(DatasetCheck(get_datasets(self.DATASETS_FILE_PATH),
                                     self.CHECKOUTS_PATH,
                                     self.DATA_PATH))

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
        experiment = self.__get_experiment()
        self.runner.add(Detect(Benchmark.COMPILES_PATH, experiment, self.config.timeout, self.config.force_detect))

    def _setup_publish_findings(self):
        experiment = self.__get_experiment()
        self.runner.add(PublishFindingsTask(experiment, self.config.dataset, Benchmark.COMPILES_PATH,
                                            self.config.review_site_url,
                                            self.config.review_site_user, self.config.review_site_password))

    def _setup_publish_metadata(self):
        self.runner.add(PublishMetadataTask(Benchmark.COMPILES_PATH, self.config.review_site_url,
                                            self.config.review_site_user, self.config.review_site_password))

    def __get_experiment(self):
        if self.config.experiment == 1:
            return ProvidedPatternsExperiment(self.__get_detector(), Benchmark.FINDINGS_PATH)
        elif self.config.experiment == 2:
            try:
                limit = self.config.limit
            except AttributeError:
                limit = 0
            return TopFindingsExperiment(self.__get_detector(), Benchmark.FINDINGS_PATH, limit)
        elif self.config.experiment == 3:
            return BenchmarkExperiment(self.__get_detector(), Benchmark.FINDINGS_PATH)

    def __get_detector(self):
        try:
            java_options = ['-' + option for option in self.config.java_options]
            return find_detector(self.DETECTORS_PATH, self.config.detector, java_options,
                                 self.config.requested_release)
        except Exception as e:
            logger.critical(e)
            exit()

    def run(self) -> None:
        self._setup_check()
        if config.task == 'info':
            self._setup_info()
        elif config.task == 'checkout':
            self._setup_checkout()
        elif config.task == 'compile':
            self._setup_checkout()
            self._setup_compile()
        elif config.task == 'detect':
            self._setup_checkout()
            self._setup_compile()
            self._setup_detect()
        elif config.task == 'publish':
            if config.publish_task == 'findings':
                self._setup_checkout()
                self._setup_compile()
                self._setup_detect()
                self._setup_publish_findings()
            elif config.publish_task == 'metadata':
                self._setup_checkout()
                self._setup_publish_metadata()
        elif config.task == 'stats':
            self._setup_stats()
        elif config.task == 'dataset-check':
            self._setup_dataset_check()

        self.runner.run()

available_detectors = get_available_detector_ids(Benchmark.DETECTORS_PATH)
available_scripts = stats.get_available_calculator_names()
available_datasets = get_available_dataset_ids(Benchmark.DATASETS_FILE_PATH)
config = command_line_util.parse_args(sys.argv, available_detectors, available_scripts, available_datasets)

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
