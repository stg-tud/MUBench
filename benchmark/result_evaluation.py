import os
import traceback
from genericpath import isdir, exists, isfile, getsize
from os import listdir
from os.path import join, splitext
from os.path import normpath, basename
from typing import Dict, Tuple, Optional, List, Union

import datareader
import settings
from utils.dotgraph_util import get_labels_from_result_file, get_labels_from_data_content
from utils.io import safe_open
from utils.logger import log_error


def evaluate_single_result(data_file: str, data_content: Dict[str, str]) -> Tuple[str, Optional[int]]:
    """
    Evaluates the result for the given misuse data
    :param data_file: The file containing the misuse data
    :param data_content: The dictionary containing the misuse data
    :return: a tuple in the form of (data_file, success) where success is 1, 0, or None (if an error occurred)
    """

    def evaluate() -> int:
        """
        Returns 1 iff the detector found the misuse; else returns 0
        :rtype: int
        """
        with safe_open(settings.LOG_FILE_RESULTS_EVALUATION, 'a+') as log:
            print("===========================================================", file=log)

            if exists(join(dir_result, settings.FILE_IGNORED)):
                print("{} was ignored by the benchmark".format(data_file), file=log)
                return

            result_file = join(dir_result, settings.FILE_DETECTOR_RESULT)
            print("Evaluating result {} against data {}".format(result_file, data_file), file=log)

            file_found = False
            label_found = False

            if exists(result_file):
                file_found = __is_file_found(result_file, data_content, log)
                label_found = __is_label_found(result_file, data_content, log)

            if file_found and label_found:
                return 1
            else:
                return 0

    dirs_results = [join(settings.RESULTS_PATH, result_dir) for result_dir in listdir(settings.RESULTS_PATH) if
                    isdir(join(settings.RESULTS_PATH, result_dir))]
    for dir_result in dirs_results:
        is_result_for_file = splitext(basename(normpath(data_file)))[0] == basename(normpath(dir_result))

        error_log = join(dir_result, settings.LOG_DETECTOR_ERROR)
        errors_occurred = exists(error_log) and isfile(error_log) and getsize(error_log) > 0

        if is_result_for_file and not errors_occurred:
            return basename(data_file), evaluate()

    return basename(data_file), None


def evaluate_results() -> Tuple[int, int, int]:
    """
    For every data files checks if the result of the misuse detection found the misuse and writes the results to a file.
    Returns -1, -1, -1 on error.
    :rtype: list
    :return: A tuple of the form: (number of data files, number of finished misuse detections, number of found misuses)
    """
    try:
        results = datareader.on_all_data_do(evaluate_single_result)

        def to_data_name(result):
            return result[0]

        def to_success(result):
            return result[1]

        applied_results = [result for result in results if result[1] is not None]

        total = len(results)
        applied = len(applied_results)
        found = sum(map(to_success, applied_results))

        def was_successful(result):
            return result[1] is 1

        def was_not_successful(result):
            return result[1] is 0

        def finished_with_error(result):
            return result[1] is None

        found_misuses = map(to_data_name, filter(was_successful, results))
        not_found_misuses = map(to_data_name, filter(was_not_successful, results))
        misuses_with_errors = map(to_data_name, filter(finished_with_error, results))

        with safe_open(settings.BENCHMARK_RESULT_FILE, 'a+') as file_result:
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
            print('These cases encountered an error (see logs for more information) or were ignored:', file=file_result)
            print('\n'.join(misuses_with_errors), file=file_result)
            print('----------------------------------------------', file=file_result)

        return total, applied, found
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        exception_string = traceback.format_exc()
        print(exception_string)
        log_error(exception_string)
        return -1, -1, -1


def normalize_data_misuse_path(misuse_file: str) -> str:
    """
    Normalizes the misuse file path (from a data file)
    :param misuse_file: The path that is given in the data file
    :rtype: str
    :return: The normalized path (can be compared to normalized result paths)
    """
    normed_misuse_file = normpath(misuse_file)

    # cut trunk folder (only for svn repositories)
    if 'trunk' + os.sep in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split('trunk' + os.sep, 1)[1]

    return normed_misuse_file


def normalize_result_misuse_path(misuse_file: str) -> str:
    """
    Normalizes the misuse file path (from a result file)
    :param misuse_file: The path that is given in the result file
    :rtype: str
    :return: The normalized path (can be compared to normalized data paths)
    """
    normed_misuse_file = normpath(misuse_file)

    # cut everything before project subfolder
    checkout_dir_prefix = settings.CHECKOUT_DIR + os.sep
    if checkout_dir_prefix in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(checkout_dir_prefix, 1)[1]

    # cut project subfolder
    if os.sep in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(os.sep, 1)[1]

    # cut trunk folder (only for svn repositories)
    if 'trunk' + os.sep in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split('trunk' + os.sep, 1)[1]

    return normed_misuse_file


def __is_file_found(result_file: str, data_content: Dict[str, Union[str, Dict]], log_stream) -> bool:
    lines = [line.rstrip('\n') for line in safe_open(result_file, 'r')]

    for line in lines:
        if line.startswith("File: "):
            # cut File: from the line to get the path
            found_misuse = line[len("File: "):]
            normed_found_misuse = normalize_result_misuse_path(found_misuse)

            for misuse_file in data_content["fix"]["files"]:
                normed_misuse_file = normalize_data_misuse_path(misuse_file["name"])

                print("{}: Comparing found misuse {}".format(normed_misuse_file, normed_found_misuse), file=log_stream)

                if normed_found_misuse == normed_misuse_file:
                    print("Match found!", file=log_stream)
                    return True
                else:
                    print("No match", file=log_stream)

    return False


def __is_label_found(result_file: str, data_content: Dict[str, Union[str, Dict]], log_stream) -> bool:
    misuse_labels = get_labels_from_data_content(data_content)
    result_labels = get_labels_from_result_file(result_file)

    # don't check if no labels are given on any end
    if not misuse_labels or not result_labels:
        return True

    for result_label in result_labels:
        is_misuse_label = result_label in misuse_labels
        if is_misuse_label:
            print("Found correct label!", file=log_stream)
            return True

    print("Correct label was not found!", file=log_stream)
    return False
