from genericpath import isdir, exists, isfile, getsize
from os import listdir
from os.path import join, splitext
from os.path import normpath, basename

import yaml
from typing import Dict, Tuple, Optional, Any, Iterable

from benchmark.utils.data_util import normalize_result_misuse_path, normalize_data_misuse_path
from benchmark.utils.dotgraph_util import get_labels
from benchmark.utils.io import safe_open
from benchmark.utils.printing import subprocess_print


class Evaluation:
    def __init__(self,
                 results_path: str,
                 detector: str,
                 detector_result_file: str,
                 checkout_base_dir: str):
        self.results_path = results_path
        self.detector = detector
        self.detector_result_file = detector_result_file
        self.checkout_base_dir = checkout_base_dir

        self.results = []

    def evaluate(self, data_file: str, data_content: Dict[str, Any]) -> Tuple[str, Optional[int]]:

        dirs_results = [join(self.results_path, result_dir) for result_dir in listdir(self.results_path) if
                        isdir(join(self.results_path, result_dir)) and not result_dir == '_LOGS']

        subprocess_print("Evaluation : running... ", end='')

        for dir_result in dirs_results:
            is_findings_for_file = splitext(basename(normpath(data_file)))[0] == basename(normpath(dir_result))

            error_log = join(dir_result, "error.log")
            errors_occurred = exists(error_log) and isfile(error_log) and getsize(error_log) > 0

            if is_findings_for_file and not errors_occurred:

                with safe_open(join(self.results_path, "_LOGS", "evaluation.log"), 'a+') as log:
                    print("===========================================================", file=log)

                    findings_file = join(dir_result, self.detector_result_file)
                    print("Evaluating result {} against data {}".format(findings_file, data_file), file=log)

                    file_found = False
                    label_found = False

                    if exists(findings_file):
                        findings = yaml.load_all(safe_open(findings_file, 'r'))

                        file_found = Evaluation.__is_file_found(findings, data_content, self.checkout_base_dir, log)
                        label_found = Evaluation.__is_label_found(findings, data_content, log)

                    if file_found and label_found:
                        print("potential hit", flush=True)
                        self.results.append((basename(data_file), 1))
                        return
                    else:
                        print("no hit", flush=True)
                        self.results.append((basename(data_file), 0))
                        return

        print("ignored (no available findings)", flush=True)
        self.results.append((basename(data_file), None))

    def output_results(self) -> None:
        if not self.results:
            return

        def to_data_name(result: Tuple[str, int]) -> str:
            return result[0]

        def to_success(result: Tuple[str, int]) -> int:
            return result[1]

        applied_results = [result for result in self.results if result[1] is not None]
        total = len(self.results)
        applied = len(applied_results)
        found = sum(map(to_success, applied_results))

        def was_successful(result: Tuple[str, int]) -> bool:
            return result[1] is 1

        def was_not_successful(result: Tuple[str, int]) -> bool:
            return result[1] is 0

        def finished_with_error(result: Tuple[str, int]) -> bool:
            return result[1] is None

        found_misuses = map(to_data_name, filter(was_successful, self.results))
        not_found_misuses = map(to_data_name, filter(was_not_successful, self.results))
        misuses_with_errors = map(to_data_name, filter(finished_with_error, self.results))
        with safe_open(join(self.results_path, "Result.txt"), 'w+') as file_result:
            print('----------------------------------------------', file=file_result)
            print('Total number of misuses in the benchmark: ' + str(total), file=file_result)
            print('Number of analyzed misuses (might be less due to ignore or errors): ' + str(applied),
                  file=file_result)
            print('Number of misuses found: ' + str(found), file=file_result)
            print('----------------------------------------------', file=file_result)
            print('These misuses were found:', file=file_result)
            print('\n'.join(found_misuses), file=file_result)
            print('----------------------------------------------', file=file_result)
            print('These misuses were not found:', file=file_result)
            print('\n'.join(not_found_misuses), file=file_result)
            print('----------------------------------------------', file=file_result)
            print('These cases encountered an error (see logs for more information) or were ignored:',
                  file=file_result)
            print('\n'.join(misuses_with_errors), file=file_result)
            print('----------------------------------------------', file=file_result)

    @staticmethod
    def __is_file_found(findings: Iterable[Dict[str, str]],
                        data_content: Dict[str, Any],
                        checkout_base_dir: str,
                        log_stream) -> bool:

        for finding in findings:
            if finding is None:
                continue

            marked_file = finding.get("file")
            if marked_file is None:
                continue

            normed_finding = normalize_result_misuse_path(marked_file, checkout_base_dir)

            for misuse_file in data_content["fix"]["files"]:
                normed_misuse_file = normalize_data_misuse_path(misuse_file["name"])

                print("{}: Comparing found misuse {}".format(normed_misuse_file, normed_finding),
                      file=log_stream)

                if normed_finding == normed_misuse_file:
                    print("Match found!", file=log_stream)
                    return True
                else:
                    print("No match", file=log_stream)

        return False

    @staticmethod
    def __is_label_found(findings: Iterable[Dict[str, str]],
                         data_content: Dict[str, Any],
                         log_stream) -> bool:

        marked_labels = []

        for finding in findings:
            if finding is None:
                continue
            graph = finding.get("graph")
            if graph is not None:
                marked_labels += get_labels(graph)

        misuse = data_content.get('misuse')

        if misuse is None:
            return True

        graph = misuse['usage']

        expected_labels = get_labels(graph)

        # don't check if no labels are given on any end
        if not expected_labels or not marked_labels:
            return True

        for marked_label in marked_labels:
            is_expected_label = marked_label in expected_labels
            if is_expected_label:
                print("Found correct label!", file=log_stream)
                return True

        print("Correct label was not found!", file=log_stream)
        return False
