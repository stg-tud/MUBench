#!/usr/bin/env python3

import logging.handlers
import os
import sys
from datetime import datetime
from os import makedirs
from os.path import join, exists, abspath, dirname

from data.detectors import find_detector, get_available_detector_ids
from data.experiments import ProvidedPatternsExperiment, TopFindingsExperiment, BenchmarkExperiment
from requirements import RequirementsCheck
from tasks.implementations import stats
from tasks.implementations.checkout import CheckoutTask
from tasks.implementations.collect_misuses import CollectMisusesTask
from tasks.implementations.collect_projects import CollectProjectsTask
from tasks.implementations.collect_versions import CollectVersionsTask
from tasks.implementations.compile import CompileTask
from tasks.implementations.dataset_check import DatasetCheckTask
from tasks.implementations.detect import DetectTask
from tasks.implementations.info import ProjectInfoTask, VersionInfoTask, MisuseInfoTask
from tasks.implementations.publish_findings import PublishFindingsTask
from tasks.implementations.publish_metadata import PublishMetadataTask
from tasks.task_runner import TaskRunner
from utils import command_line_util
from utils.data_entity_lists import DataEntityLists
from utils.data_filter import DataFilter
from utils.dataset_util import get_available_datasets, get_available_dataset_ids, get_white_list
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

        self.white_list = []
        self.black_list = []
        if 'white_list' in config:
            self.white_list.extend(config.white_list)
        if 'black_list' in config:
            self.black_list.extend(config.black_list)

        self.data_entity_lists = DataEntityLists(self.white_list, self.black_list)

        if 'dataset' in config:
            self.white_list.extend(get_white_list(self.DATASETS_FILE_PATH, config.dataset))

    def run(self) -> None:
        RequirementsCheck()

        tasks = []
        data_filter = DataFilter(self.white_list, self.black_list)

        if config.task == 'info':
            project_info = ProjectInfoTask(Benchmark.CHECKOUTS_PATH, benchmark.COMPILES_PATH)
            version_info = VersionInfoTask(Benchmark.CHECKOUTS_PATH, benchmark.COMPILES_PATH)
            misuse_info = MisuseInfoTask(Benchmark.CHECKOUTS_PATH, benchmark.COMPILES_PATH)
            tasks.append(CollectProjectsTask(benchmark.DATA_PATH, self.data_entity_lists))
            tasks.append(project_info)
            tasks.append(CollectVersionsTask(self.data_entity_lists))
            tasks.append(version_info)
            tasks.append(CollectMisusesTask(data_filter))
            tasks.append(misuse_info)
        elif config.task == 'checkout':
            tasks.append(CollectProjectsTask(benchmark.DATA_PATH, self.data_entity_lists))
            tasks.append(CollectVersionsTask(self.data_entity_lists))
            tasks.append(CheckoutTask(Benchmark.CHECKOUTS_PATH, self.config.force_checkout, self.config.use_tmp_wrkdir))
        elif config.task == 'compile':
            tasks.append(CollectProjectsTask(benchmark.DATA_PATH, self.data_entity_lists))
            tasks.append(CollectVersionsTask(self.data_entity_lists))
            tasks.append(CheckoutTask(Benchmark.CHECKOUTS_PATH, self.config.force_checkout, self.config.use_tmp_wrkdir))
            tasks.append(CompileTask(Benchmark.COMPILES_PATH, self.config.force_compile, self.config.use_tmp_wrkdir))
        elif config.task == 'detect':
            tasks.append(CollectProjectsTask(benchmark.DATA_PATH, self.data_entity_lists))
            tasks.append(CollectVersionsTask(self.data_entity_lists))
            tasks.append(CheckoutTask(Benchmark.CHECKOUTS_PATH, self.config.force_checkout, self.config.use_tmp_wrkdir))
            tasks.append(CompileTask(Benchmark.COMPILES_PATH, self.config.force_compile, self.config.use_tmp_wrkdir))
            tasks.append(
                DetectTask(Benchmark.COMPILES_PATH, self.__get_experiment(), self.config.timeout,
                           self.config.force_detect))
        elif config.task == 'publish':
            if config.publish_task == 'findings':
                tasks.append(CollectProjectsTask(benchmark.DATA_PATH, self.data_entity_lists))
                tasks.append(CollectVersionsTask(self.data_entity_lists))
                tasks.append(
                    CheckoutTask(Benchmark.CHECKOUTS_PATH, self.config.force_checkout, self.config.use_tmp_wrkdir))
                tasks.append(
                    CompileTask(Benchmark.COMPILES_PATH, self.config.force_compile, self.config.use_tmp_wrkdir))
                tasks.append(DetectTask(Benchmark.COMPILES_PATH, self.__get_experiment(), self.config.timeout,
                                        self.config.force_detect))
                tasks.append(CollectMisusesTask(data_filter))
                tasks.append(PublishFindingsTask(self.__get_experiment(), self.config.dataset, Benchmark.COMPILES_PATH,
                                                 self.config.review_site_url, self.config.review_site_user,
                                                 self.config.review_site_password))
            elif config.publish_task == 'metadata':
                tasks.append(CollectProjectsTask(benchmark.DATA_PATH, self.data_entity_lists))
                tasks.append(CollectVersionsTask(self.data_entity_lists))
                tasks.append(
                    CheckoutTask(Benchmark.CHECKOUTS_PATH, self.config.force_checkout, self.config.use_tmp_wrkdir))
                tasks.append(CollectMisusesTask(data_filter))
                tasks.append(
                    PublishMetadataTask(Benchmark.COMPILES_PATH, self.config.review_site_url,
                                        self.config.review_site_user,
                                        self.config.review_site_password))
        elif config.task == 'stats':
            tasks.append(CollectProjectsTask(benchmark.DATA_PATH, self.data_entity_lists))
            tasks.append(CollectVersionsTask(self.data_entity_lists))
            tasks.append(CollectMisusesTask(data_filter))
            tasks.append(stats.get_calculator(self.config.script))
        elif config.task == 'dataset-check':
            tasks.append(CollectProjectsTask(benchmark.DATA_PATH, self.data_entity_lists))
            tasks.append(CollectVersionsTask(self.data_entity_lists))
            tasks.append(CollectMisusesTask(data_filter))
            tasks.append(
                DatasetCheckTask(get_available_datasets(self.DATASETS_FILE_PATH), self.CHECKOUTS_PATH, self.DATA_PATH))

        runner = TaskRunner(tasks)
        runner.run()

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
