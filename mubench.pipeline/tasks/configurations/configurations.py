from typing import List

from data.detectors import find_detector
from tasks.implementations import stats
from tasks.implementations.checkout import CheckoutTask
from tasks.implementations.collect_misuses import CollectMisusesTask
from tasks.implementations.collect_projects import CollectProjectsTask
from tasks.implementations.collect_versions import CollectVersionsTask
from tasks.implementations.compile_misuse import CompileMisuseTask
from tasks.implementations.compile_version import CompileVersionTask
from tasks.implementations.dataset_check import DatasetCheckTask
from tasks.implementations.detect_all_findings import DetectAllFindingsTask
from tasks.implementations.detect_providing_patterns import DetectProvidingPatternsTask
from tasks.implementations.findings_filters import AllFindingsFilterTask, PotentialHitsFilterTask
from tasks.implementations.info import ProjectInfoTask, VersionInfoTask, MisuseInfoTask
from tasks.implementations.publish_findings import PublishFindingsTask
from tasks.implementations.publish_metadata import PublishMetadataTask
from utils.dataset_util import get_available_datasets


class TaskConfiguration:
    @staticmethod
    def mode() -> str:
        raise NotImplementedError

    def tasks(self, config) -> List:
        raise NotImplementedError


def get_task_configuration(config) -> List:
    if hasattr(config, 'sub_task'):
        mode = "{} {}".format(config.task, config.sub_task)
    else:
        mode = config.task

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
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask()
        collect_misuses = CollectMisusesTask()
        project_info = ProjectInfoTask(config.checkouts_path, config.compiles_path)
        version_info = VersionInfoTask(config.checkouts_path, config.compiles_path)
        misuse_info = MisuseInfoTask(config.checkouts_path, config.compiles_path)
        return [collect_projects, project_info, collect_versions, version_info, collect_misuses, misuse_info]


class CheckoutTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "checkout"

    def tasks(self, config):
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask()
        checkout = CheckoutTask(config.checkouts_path, config.force_checkout, config.use_tmp_wrkdir)
        return [collect_projects, collect_versions, checkout]


class CompileTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "compile"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask()
        collect_misuses = CollectMisusesTask()
        checkout = CheckoutTask(config.checkouts_path, config.force_checkout, config.use_tmp_wrkdir)
        compile_version = CompileVersionTask(config.compiles_path, config.force_compile, config.use_tmp_wrkdir)
        compile_misuse = CompileMisuseTask(config.compiles_path, config.force_compile)

        return [collect_projects, collect_versions, checkout, compile_version, collect_misuses, compile_misuse]


class RunProvidedPatternsExperiment(TaskConfiguration):
    ID = "ex1"

    @staticmethod
    def mode() -> str:
        return "run {}".format(RunProvidedPatternsExperiment.ID)

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask()
        checkout = CheckoutTask(config.checkouts_path, config.force_checkout, config.use_tmp_wrkdir)
        compile_version = CompileVersionTask(config.compiles_path, config.force_compile, config.use_tmp_wrkdir)
        collect_misuses = CollectMisusesTask()
        compile_misuse = CompileMisuseTask(config.compiles_path, config.force_compile)
        detect = DetectProvidingPatternsTask(_get_detector(config), config.findings_path, config.force_detect,
                                             config.timeout)
        return [collect_projects, collect_versions, checkout, compile_version, collect_misuses, compile_misuse, detect]


class PublishProvidedPatternsExperiment(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish {}".format(RunProvidedPatternsExperiment.ID)

    def tasks(self, config) -> List:
        filter_ = PotentialHitsFilterTask()
        publish = PublishFindingsTask(RunProvidedPatternsExperiment.ID, config.dataset, config.compiles_path,
                                      config.review_site_url, config.review_site_user, config.review_site_password)
        return RunProvidedPatternsExperiment().tasks(config) + [filter_, publish]


class RunAllFindingsExperiment(TaskConfiguration):
    ID = "ex2"

    @staticmethod
    def mode() -> str:
        return "run {}".format(RunAllFindingsExperiment.ID)

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask()
        checkout = CheckoutTask(config.checkouts_path, config.force_checkout, config.use_tmp_wrkdir)
        compile_version = CompileVersionTask(config.compiles_path, config.force_compile, config.use_tmp_wrkdir)
        detect = DetectAllFindingsTask(config.compiles_path, config.findings_path, _get_detector(config),
                                       config.timeout, config.force_detect, config.limit)
        return [collect_projects, collect_versions, checkout, compile_version, detect]


class PublishAllFindingsExperiment(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish {}".format(RunAllFindingsExperiment.ID)

    def tasks(self, config) -> List:
        filter_ = AllFindingsFilterTask()
        publish = PublishFindingsTask(RunAllFindingsExperiment.ID, config.dataset, config.compiles_path,
                                      config.review_site_url, config.review_site_user, config.review_site_password)
        return RunAllFindingsExperiment().tasks(config) + [filter_, publish]


class RunBenchmarkExperiment(TaskConfiguration):
    ID = "ex3"

    @staticmethod
    def mode() -> str:
        return "run {}".format(RunBenchmarkExperiment.ID)

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask()
        checkout = CheckoutTask(config.checkouts_path, config.force_checkout, config.use_tmp_wrkdir)
        compile_version = CompileVersionTask(config.compiles_path, config.force_compile, config.use_tmp_wrkdir)
        detect = DetectAllFindingsTask(config.compiles_path, config.findings_path, _get_detector(config),
                                       config.timeout, config.force_detect, config.limit)
        return [collect_projects, collect_versions, checkout, compile_version, detect]


class PublishBenchmarkExperiment(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish {}".format(RunBenchmarkExperiment.ID)

    def tasks(self, config) -> List:
        collect_misuses = CollectMisusesTask()
        filter_ = PotentialHitsFilterTask()
        publish = PublishFindingsTask(RunBenchmarkExperiment.ID, config.dataset, config.compiles_path,
                                      config.review_site_url, config.review_site_user, config.review_site_password)
        return RunBenchmarkExperiment().tasks(config) + [collect_misuses, filter_, publish]


class PublishMetadataTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish metadata"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask()
        checkout = CheckoutTask(config.checkouts_path, config.force_checkout, config.use_tmp_wrkdir)
        collect_misuses = CollectMisusesTask()
        publish = PublishMetadataTask(config.compiles_path, config.review_site_url, config.review_site_user,
                                      config.review_site_password)
        return [collect_projects, collect_versions, checkout, collect_misuses, publish]


class StatsTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "stats"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask()
        collect_misuses = CollectMisusesTask()
        calculator = stats.get_calculator(config.script)
        return [collect_projects, collect_versions, collect_misuses, calculator]


class DatasetCheckTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "dataset-check"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask()
        collect_misuses = CollectMisusesTask()
        dataset_check = DatasetCheckTask(get_available_datasets(config.datasets_file_path), config.checkouts_path,
                                         config.data_path)
        return [collect_projects, collect_versions, collect_misuses, dataset_check]


def _get_detector(config):
    java_options = ['-' + option for option in config.java_options]
    return find_detector(config.detectors_path, config.detector, java_options, config.requested_release)
