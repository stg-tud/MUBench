#!/usr/bin/env python3
# coding=utf-8
import csv
from os import listdir
from os.path import exists, join, isdir, basename
from typing import Dict
from typing import Set

from benchmark.utils import csv_util


class Visualizer:
    def __init__(self, results_base_path: str, reviewed_eval_result_file: str, result_file: str):
        self.results_base_path = results_base_path
        self.reviewed_eval_result_file = reviewed_eval_result_file
        self.result_file = result_file

    def run(self):
        if not exists(self.results_base_path):
            exit("No results found.")

        results = dict()  # type: Dict[str, Dict[str, str]]
        misuses = set()  # type: Set[str]

        for detector_result_dir in self.__get_immediate_subdirs(self.results_base_path):
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
            exit("No results found.")

        headers = ['Detector'] + sorted(list(misuses))
        file = join(self.results_base_path, self.result_file)
        csv_util.write_table(file, headers, results)

    @staticmethod
    def __get_immediate_subdirs(directory: str):
        return [join(directory, subdir) for subdir in listdir(directory) if isdir(join(directory, subdir))]
