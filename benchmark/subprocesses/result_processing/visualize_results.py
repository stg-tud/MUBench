#!/usr/bin/env python3
# coding=utf-8
import csv
import logging
from os import listdir
from os.path import exists, join, isdir, basename
from typing import Dict, Iterable, Optional
from typing import List
from typing import Set

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.utils import csv_util


class Grouping:
    @staticmethod
    def get_available_groupings() -> Iterable[type]:
        # noinspection PyUnresolvedReferences
        import benchmark.subprocesses.result_processing.groupings.groupings
        return Grouping.__subclasses__()

    @staticmethod
    def get_available_grouping_names() -> Iterable[str]:
        return [grouping.__name__ for grouping in Grouping.get_available_groupings()]

    @staticmethod
    def get_by_name(name: str) -> Optional[type]:
        for grouping in Grouping.get_available_groupings():
            if grouping.__name__ == name:
                return grouping

        return None

    def get_groups(self, misuse: Misuse) -> Iterable[str]:
        raise NotImplementedError


class Visualizer:
    def __init__(self, results_base_path: str, reviewed_eval_result_file: str, result_file: str, data_path: str):
        self.results_base_path = results_base_path
        self.reviewed_eval_result_file = reviewed_eval_result_file
        self.result_file = result_file
        self.data_path = data_path
        self.detector_header = 'Detector'

    def create(self):
        logger = logging.getLogger()

        if not exists(self.results_base_path):
            logger.error("No results found.")
            return

        results = dict()  # type: Dict[str, Dict[str, str]]
        misuses = set()  # type: Set[str]

        for detector_result_dir in self.__get_immediate_subdirs(self.results_base_path):
            logger.info("Adding results: %s", detector_result_dir)
            reviewed_eval_result_file = join(detector_result_dir, self.reviewed_eval_result_file)
            if not exists(reviewed_eval_result_file):
                continue

            detector_result = dict()  # type: Dict[str, str]
            with open(reviewed_eval_result_file) as reviewed_eval_result:
                csvreader = csv.reader(reviewed_eval_result, quotechar='|')
                for row in csvreader:
                    misuse, result = row
                    detector_result[misuse] = result
                    misuses.add(misuse)

            detector = basename(detector_result_dir)
            results[detector] = detector_result

        if not results:
            logger.error("No results found.")
            return

        headers = [self.detector_header] + sorted(list(misuses))
        file = join(self.results_base_path, self.result_file)
        csv_util.write_table(file, headers, results)
        self.write_all_groupings()

    def write_all_groupings(self):
        for grouping in Grouping.get_available_groupings():
            self.group('result-{}.csv'.format(grouping.__name__), grouping())

    def group(self, target_file: str, grouping: Grouping):
        logger = logging.getLogger()
        logger.info("Grouping by rule %s", type(grouping).__name__)

        merged_result_file = join(self.results_base_path, self.result_file)

        # TODO: implicitly run visualize in this case?
        if not exists(merged_result_file):
            exit("No result file available! Please run `visualize` to generate it.")

        results = csv_util.read_table(merged_result_file, self.detector_header)  # type: Dict[str, Dict[str, str]]

        grouped_results = dict()  # type: Dict[str, Dict[str, str]]
        all_groups = set()  # type: Set[str]

        for detector, results_per_misuse in results.items():
            logger.info("    Grouping results for detector %s", detector)

            grouped_results[detector] = dict()
            results_per_group = dict()  # type: Dict[str, List[int]]

            for misuse_name, result_as_str in results_per_misuse.items():
                misuse_name = misuse_name.lstrip("'").rstrip("'")
                misuse_path = join(self.data_path, misuse_name)
                if not Misuse.is_misuse(misuse_path):
                    logger.error("Couldn't validate misuse %s", misuse_path)
                    continue

                result = int(result_as_str)  # type: int
                groups = grouping.get_groups(Misuse(self.data_path, Project.MISUSES_DIR, misuse_name))

                for group in groups:
                    if group not in results_per_group:
                        results_per_group[group] = [result]
                    else:
                        results_per_group[group].append(result)

                    all_groups.add(group)

            for group, results_for_group in results_per_group.items():
                average = sum(results_for_group) / len(results_for_group)
                grouped_results[detector][group] = average

        headers = [self.detector_header] + sorted(list(all_groups))
        file = join(self.results_base_path, target_file)
        csv_util.write_table(file, headers, grouped_results)

    @staticmethod
    def __get_immediate_subdirs(directory: str):
        return [join(directory, subdir) for subdir in listdir(directory) if isdir(join(directory, subdir))]
