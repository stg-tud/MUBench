from typing import List

from data.detectors import find_detector
from data.experiments import ProvidedPatternsExperiment, TopFindingsExperiment, BenchmarkExperiment
from tasks.implementations import stats
from tasks.implementations.checkout import CheckoutTask
from tasks.implementations.collect_misuses import CollectMisusesTask
from tasks.implementations.collect_projects import CollectProjectsTask
from tasks.implementations.collect_versions import CollectVersionsTask
from tasks.implementations.compile_version import CompileVersionTask
from tasks.implementations.compile_misuse import CompileMisuseTask
from tasks.implementations.dataset_check import DatasetCheckTask
from tasks.implementations.detect import DetectTask
from tasks.implementations.info import ProjectInfoTask, VersionInfoTask, MisuseInfoTask
from tasks.implementations.publish_findings import PublishFindingsTask
from tasks.implementations.publish_metadata import PublishMetadataTask
from tasks.task_runner import TaskRunner
from utils.dataset_util import get_available_datasets


class TaskConfiguration:
    @staticmethod
    def mode() -> str:
        raise NotImplementedError

    def tasks(self, config) -> List:
        raise NotImplementedError


def get_task_configuration(config) -> List:
    mode = config.task
    if hasattr(config, 'publish_task'):
        mode += " " + config.publish_task

    requested_configurations = [task_config() for task_config in
                                TaskConfiguration.__subclasses__() if task_config.mode() == mode]
    if len(requested_configurations) > 1:
        raise ValueError("Multiple configurations for {}".format(mode))
    if len(requested_configurations) == 0:
        raise ValueError("No configuration available for {}".format(mode))

    return requested_configurations[0].tasks(config)


class InfoTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "info"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.DATA_PATH)
        collect_versions = CollectVersionsTask()
        collect_misuses = CollectMisusesTask()
        project_info = ProjectInfoTask(config.CHECKOUTS_PATH, config.COMPILES_PATH)
        version_info = VersionInfoTask(config.CHECKOUTS_PATH, config.COMPILES_PATH)
        misuse_info = MisuseInfoTask(config.CHECKOUTS_PATH, config.COMPILES_PATH)
        return [collect_projects, project_info, collect_versions, version_info, collect_misuses, misuse_info]


class CheckoutTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "checkout"

    def tasks(self, config):
        collect_projects = CollectProjectsTask(config.DATA_PATH)
        collect_versions = CollectVersionsTask()
        checkout = CheckoutTask(config.CHECKOUTS_PATH, config.force_checkout, config.use_tmp_wrkdir)
        return [collect_projects, collect_versions, checkout]


class CompileTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "compile"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.DATA_PATH)
        collect_versions = CollectVersionsTask()
        collect_misuses = CollectMisusesTask()
        checkout = CheckoutTask(config.CHECKOUTS_PATH, config.force_checkout, config.use_tmp_wrkdir)
        compile_version = CompileVersionTask(config.COMPILES_PATH, config.force_compile, config.use_tmp_wrkdir)
        compile_misuse = CompileMisuseTask(config.COMPILES_PATH, config.force_compile)

        return [collect_projects, collect_versions, checkout, compile_version, collect_misuses, compile_misuse]


class DetectTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "detect"

    def tasks(self, config) -> List:
        experiment = _get_experiment(config)

        collect_projects = CollectProjectsTask(config.DATA_PATH)
        collect_versions = CollectVersionsTask()
        checkout = CheckoutTask(config.CHECKOUTS_PATH, config.force_checkout, config.use_tmp_wrkdir)
        compile_version = CompileVersionTask(config.COMPILES_PATH, config.force_compile, config.use_tmp_wrkdir)
        detect = DetectTask(config.COMPILES_PATH, experiment, config.timeout, config.force_detect)

        if experiment.ID == ProvidedPatternsExperiment.ID:
            compile_misuse = CompileMisuseTask(config.COMPILES_PATH, config.force_compile)
            return [collect_projects, collect_versions, checkout, compile_version,
                    TaskRunner([CollectMisusesTask(), compile_misuse]), detect]

        return [collect_projects, collect_versions, checkout, compile_version, detect]


class PublishFindingsTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish findings"

    def tasks(self, config) -> List:
        experiment = _get_experiment(config)

        collect_projects = CollectProjectsTask(config.DATA_PATH)
        collect_versions = CollectVersionsTask()
        checkout = CheckoutTask(config.CHECKOUTS_PATH, config.force_checkout, config.use_tmp_wrkdir)
        compile_version = CompileVersionTask(config.COMPILES_PATH, config.force_compile, config.use_tmp_wrkdir)
        detect = DetectTask(config.COMPILES_PATH, experiment, config.timeout, config.force_detect)
        publish = PublishFindingsTask(_get_experiment(config), config.dataset, config.COMPILES_PATH,
                                      config.review_site_url, config.review_site_user, config.review_site_password)

        if experiment.ID == ProvidedPatternsExperiment.ID:
            compile_misuse = CompileMisuseTask(config.COMPILES_PATH, config.force_compile)
            return [collect_projects, collect_versions, checkout, compile_version,
                    TaskRunner([CollectMisusesTask(), compile_misuse]), detect, publish]

        return [collect_projects, collect_versions, checkout, compile_version, detect, publish]


class PublishMetadataTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish metadata"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.DATA_PATH)
        collect_versions = CollectVersionsTask()
        checkout = CheckoutTask(config.CHECKOUTS_PATH, config.force_checkout, config.use_tmp_wrkdir)
        collect_misuses = CollectMisusesTask()
        publish = PublishMetadataTask(config.COMPILES_PATH, config.review_site_url, config.review_site_user,
                                      config.review_site_password)
        return [collect_projects, collect_versions, checkout, collect_misuses, publish]


class StatsTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "stats"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.DATA_PATH)
        collect_versions = CollectVersionsTask()
        collect_misuses = CollectMisusesTask()
        calculator = stats.get_calculator(config.script)
        return [collect_projects, collect_versions, collect_misuses, calculator]


class DatasetCheckTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "dataset-check"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.DATA_PATH)
        collect_versions = CollectVersionsTask()
        collect_misuses = CollectMisusesTask()
        dataset_check = DatasetCheckTask(get_available_datasets(config.DATASETS_FILE_PATH), config.CHECKOUTS_PATH,
                                         config.DATA_PATH)
        return [collect_projects, collect_versions, collect_misuses, dataset_check]


def _get_experiment(config):
    if config.experiment == 1:
        return ProvidedPatternsExperiment(__get_detector(config), config.FINDINGS_PATH)
    elif config.experiment == 2:
        try:
            limit = config.limit
        except AttributeError:
            limit = 0
        return TopFindingsExperiment(__get_detector(config), config.FINDINGS_PATH, limit)
    elif config.experiment == 3:
        return BenchmarkExperiment(__get_detector(config), config.FINDINGS_PATH)


def __get_detector(config):
    java_options = ['-' + option for option in config.java_options]
    return find_detector(config.DETECTORS_PATH, config.detector, java_options, config.requested_release)
