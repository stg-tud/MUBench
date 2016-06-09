from genericpath import exists, isfile, getsize
from os.path import join

import yaml
from typing import Dict, Tuple, Optional, Any, Iterable

from benchmark.datareader import DataReader
from benchmark.misuse import Misuse
from benchmark.utils.data_util import normalize_result_misuse_path, normalize_data_misuse_path
from benchmark.utils.dotgraph_util import get_labels
from benchmark.utils.io import safe_open
from benchmark.utils.printing import subprocess_print


class Evaluation:
    def __init__(self,
                 results_path: str,
                 detector_result_file: str,
                 checkout_base_dir: str):
        self.results_path = results_path
        self.detector_result_file = detector_result_file
        self.checkout_base_dir = checkout_base_dir

        self.results = []

    def evaluate(self, misuse: Misuse) -> Tuple[str, Optional[int]]:

        subprocess_print("Evaluation : running... ", end='')

        dir_result = join(self.results_path, misuse.name)

        error_log = join(dir_result, "error.log")
        errors_occurred = exists(error_log) and isfile(error_log) and getsize(error_log) > 0

        if not errors_occurred:
            with safe_open(join(dir_result, "evaluation.log"), 'a+') as log:
                print("===========================================================", file=log)

                findings_file = join(dir_result, self.detector_result_file)
                print("Evaluating result {}".format(findings_file), file=log)

                file_found = False
                label_found = False

                if exists(findings_file):
                    findings = yaml.load_all(safe_open(findings_file, 'r'))

                    src_prefix = None if misuse.build_config is None else misuse.build_config.src

                    file_found = Evaluation.__is_file_found(findings, misuse.meta,
                                                            join(self.checkout_base_dir, misuse.project_name),
                                                            src_prefix, log)
                    label_found = Evaluation.__is_label_found(findings, misuse.meta, log)

                if file_found and label_found:
                    print("potential hit", flush=True)
                    self.results.append((misuse.name, 1))
                    return DataReader.Result.ok
                else:
                    print("no hit", flush=True)
                    self.results.append((misuse.name, 0))
                    return DataReader.Result.ok

        print("ignored (no available findings)", flush=True)
        self.results.append((misuse.name, None))
        return DataReader.Result.ok

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
                        checkout_dir: str,
                        src_prefix: Optional[str],
                        log_stream) -> bool:

        for finding in findings:
            if finding is None:
                continue

            marked_file = finding.get("file")
            if marked_file is None:
                continue

            normed_finding = normalize_result_misuse_path(marked_file, checkout_dir, src_prefix)

            for misuse_file in data_content["fix"]["files"]:
                normed_misuse_file = normalize_data_misuse_path(misuse_file["name"], src_prefix)

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
