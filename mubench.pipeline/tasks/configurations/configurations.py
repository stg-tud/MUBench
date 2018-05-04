from typing import List

from tasks.implementations.crossproject_create_index import CrossProjectCreateIndexTask
from tasks.implementations import stats
from tasks.implementations.checkout import CheckoutTask
from tasks.implementations.collect_misuses import CollectMisusesTask
from tasks.implementations.collect_projects import CollectProjectsTask
from tasks.implementations.collect_versions import CollectVersionsTask
from tasks.implementations.compile_misuse import CompileMisuseTask
from tasks.implementations.compile_version import CompileVersionTask
from tasks.implementations.crossproject_create_project_list import CrossProjectCreateProjectListTask
from tasks.implementations.crossproject_prepare import CrossProjectPrepareTask
from tasks.implementations.crossproject_read_index import CrossProjectReadIndexTask, CrossProjectReadIndexPerMisuseTask, \
    CrossProjectReadIndexPerVersionTask, CrossProjectSkipReadIndexTask
from tasks.implementations.dataset_check_misuse import MisuseCheckTask
from tasks.implementations.dataset_check_project import ProjectCheckTask
from tasks.implementations.dataset_check_version import VersionCheckTask
from tasks.implementations.detect_all_findings import DetectAllFindingsTask
from tasks.implementations.detect_provided_correct_usages import DetectProvidedCorrectUsagesTask
from tasks.implementations.filter_misuses_without_correct_usages import FilterMisusesWithoutCorrectUsagesTask
from tasks.implementations.findings_filters import AllFindingsFilterTask, PotentialHitsFilterTask
from tasks.implementations.info import ProjectInfoTask, VersionInfoTask, MisuseInfoTask
from tasks.implementations.load_detector import LoadDetectorTask
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
        collect_versions = CollectVersionsTask(config.development_mode)
        collect_misuses = CollectMisusesTask()
        project_info = ProjectInfoTask(config.checkouts_path, config.compiles_path)
        version_info = VersionInfoTask(config.checkouts_path, config.compiles_path)
        misuse_info = MisuseInfoTask(config.checkouts_path, config.compiles_path)
        return [collect_projects, project_info, collect_versions, version_info, collect_misuses, misuse_info]


class CheckoutTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "checkout"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask(config.development_mode)
        checkout = CheckoutTask(config.checkouts_path, config.run_timestamp, config.force_checkout, config.use_tmp_wrkdir)
        return [collect_projects, collect_versions, checkout]


class CompileTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "compile"

    def tasks(self, config) -> List:
        compile_version = CompileVersionTask(config.compiles_path, config.run_timestamp, config.force_compile,
                                             config.use_tmp_wrkdir)
        collect_misuses = CollectMisusesTask()
        compile_misuse = CompileMisuseTask(config.compiles_path, config.run_timestamp, config.force_compile)
        return CheckoutTaskConfiguration().tasks(config) + [compile_version, collect_misuses, compile_misuse]


class RunProvidedPatternsExperiment(TaskConfiguration):
    ID = "ex1"

    @staticmethod
    def mode() -> str:
        return "run {}".format(RunProvidedPatternsExperiment.ID)

    def tasks(self, config) -> List:
        compile_version = CompileVersionTask(config.compiles_path, config.run_timestamp, config.force_compile,
                                             config.use_tmp_wrkdir)
        collect_misuses = CollectMisusesTask()
        filter_misuses_without_correct_usages = FilterMisusesWithoutCorrectUsagesTask()
        compile_misuse = CompileMisuseTask(config.compiles_path, config.run_timestamp, config.force_compile)
        load_detector = LoadDetectorTask(config.detectors_path, config.detector, config.requested_release,
                                         config.java_options)
        detect = DetectProvidedCorrectUsagesTask(config.findings_path, config.force_detect, config.timeout,
                                                 config.run_timestamp)

        # noinspection PyTypeChecker
        return [load_detector] + CheckoutTaskConfiguration().tasks(config) + \
               [compile_version, collect_misuses, filter_misuses_without_correct_usages, compile_misuse] + [detect]


class PublishProvidedPatternsExperiment(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish {}".format(RunProvidedPatternsExperiment.ID)

    def tasks(self, config) -> List:
        filter_ = PotentialHitsFilterTask()
        publish = PublishFindingsTask(RunProvidedPatternsExperiment.ID, config.compiles_path, config.review_site_url,
                                      config.review_site_user, config.review_site_password)
        return RunProvidedPatternsExperiment().tasks(config) + [filter_, publish]


class RunAllFindingsExperiment(TaskConfiguration):
    ID = "ex2"

    @staticmethod
    def mode() -> str:
        return "run {}".format(RunAllFindingsExperiment.ID)

    def tasks(self, config) -> List:
        compile_version = CompileVersionTask(config.compiles_path, config.run_timestamp,
                                             config.force_compile, config.use_tmp_wrkdir)
        load_detector = LoadDetectorTask(config.detectors_path, config.detector, config.requested_release,
                                         config.java_options)
        detect = DetectAllFindingsTask(config.findings_path, config.force_detect, config.timeout, config.run_timestamp)
        return [load_detector] + CheckoutTaskConfiguration().tasks(config) + [compile_version, detect]


class PublishAllFindingsExperiment(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish {}".format(RunAllFindingsExperiment.ID)

    def tasks(self, config) -> List:
        filter_ = AllFindingsFilterTask(config.limit)
        publish = PublishFindingsTask(RunAllFindingsExperiment.ID, config.compiles_path, config.review_site_url,
                                      config.review_site_user, config.review_site_password)
        return RunAllFindingsExperiment().tasks(config) + [filter_, publish]


class RunBenchmarkExperiment(TaskConfiguration):
    ID = "ex3"

    @staticmethod
    def mode() -> str:
        return "run {}".format(RunBenchmarkExperiment.ID)

    def tasks(self, config) -> List:
        compile_version = CompileVersionTask(config.compiles_path, config.run_timestamp,
                                             config.force_compile, config.use_tmp_wrkdir)
        load_detector = LoadDetectorTask(config.detectors_path, config.detector, config.requested_release,
                                         config.java_options)
        detect = DetectAllFindingsTask(config.findings_path, config.force_detect, config.timeout, config.run_timestamp)

        read_index = CrossProjectReadIndexPerVersionTask(config.xp_index_file) if config.with_xp \
            else CrossProjectSkipReadIndexTask()
        prepare_cross_project = [CrossProjectCreateIndexTask(config.xp_index_file),
                                 read_index,
                                 CrossProjectPrepareTask(config.root_path, config.xp_checkouts_path,
                                                         config.run_timestamp,
                                                         config.max_project_sample_size, config.boa_user,
                                                         config.boa_password)]

        # noinspection PyTypeChecker
        return [load_detector] + CheckoutTaskConfiguration().tasks(config) + [compile_version] + \
            prepare_cross_project + [detect]


class RunCrossProjectPrepare(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "checkout-xp"

    def tasks(self, config) -> List:
        create_index_tasks = [CollectProjectsTask(config.data_path), CollectVersionsTask(config.development_mode),
                              CollectMisusesTask(), CrossProjectCreateIndexTask(config.xp_index_file)]
        create_index = TaskRunner(create_index_tasks)
        # noinspection PyTypeChecker
        return [create_index,
                CrossProjectReadIndexTask(config.xp_index_file),
                CrossProjectPrepareTask(config.root_path, config.xp_checkouts_path, config.run_timestamp, config.max_project_sample_size, config.boa_user,
                                        config.boa_password),
                CrossProjectCreateProjectListTask(config.root_path, config.xp_index_file, config.xp_checkouts_path)]


class PublishBenchmarkExperiment(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish {}".format(RunBenchmarkExperiment.ID)

    def tasks(self, config) -> List:
        collect_misuses = CollectMisusesTask()
        filter_ = PotentialHitsFilterTask()
        publish = PublishFindingsTask(RunBenchmarkExperiment.ID, config.compiles_path, config.review_site_url,
                                      config.review_site_user, config.review_site_password)
        return RunBenchmarkExperiment().tasks(config) + [collect_misuses, filter_, publish]


class PublishMetadataTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "publish metadata"

    def tasks(self, config) -> List:
        collect_misuses = CollectMisusesTask()
        publish = PublishMetadataTask(config.checkouts_path, config.review_site_url, config.review_site_user,
                                      config.review_site_password)
        return CheckoutTaskConfiguration().tasks(config) + [collect_misuses, publish]


class StatsTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "stats"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask(config.development_mode)
        collect_misuses = CollectMisusesTask()
        calculator = stats.get_calculator(config.script)
        return [collect_projects, collect_versions, collect_misuses, calculator]


class SetupCheckTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "check setup"

    def tasks(self, config) -> List:
        return []


class DatasetCheckTaskConfiguration(TaskConfiguration):
    @staticmethod
    def mode() -> str:
        return "check dataset"

    def tasks(self, config) -> List:
        collect_projects = CollectProjectsTask(config.data_path)
        collect_versions = CollectVersionsTask(config.development_mode)
        collect_misuses = CollectMisusesTask()
        project_check = ProjectCheckTask()
        version_check = VersionCheckTask()
        misuse_check = MisuseCheckTask(get_available_datasets(config.datasets_file_path), config.checkouts_path,
                                       config.data_path)
        return [collect_projects, project_check, collect_versions, version_check, collect_misuses, misuse_check]
