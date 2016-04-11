import os
import traceback
from genericpath import isdir, exists, isfile, getsize
from os import listdir
from os.path import join, splitext
from os.path import normpath, basename

import datareader
import settings
from utils.io import safe_open
from utils.logger import log_error


def evaluate_single_result(data_file: str, data_content: dict):
    """
    Evaluates the result for the given misuse data
    :param data_file: The file containing the misuse data
    :param data_content: The dictionary containing the misuse data
    :return: a tuple in the form of (data_file, success) where success is 1, 0, or None (if an error occurred)
    """

    def evaluate():
        """
        Returns 1 iff the detector found the misuse; else returns 0
        :rtype: int
        """
        with safe_open(settings.LOG_FILE_RESULTS_EVALUATION, 'a+') as log:
            print("===========================================================", file=log)

            if exists(join(dir_result, settings.FILE_IGNORED)):
                print("{} was ignored by the benchmark".format(data_file), file=log)
                return

            file_result = join(dir_result, settings.FILE_DETECTOR_RESULT)
            print("Evaluating result {} against data {}".format(file_result, data_file), file=log)

            for fix_file in data_content["fix"]["files"]:
                normed_misuse_file = normalize_data_misuse_path(fix_file["name"])

                print("Looking for file {}".format(normed_misuse_file), file=log)

                if exists(file_result):
                    lines = [line.rstrip('\n') for line in safe_open(file_result, 'r')]

                    for line in lines:
                        if line.startswith("File: "):
                            # cut File: from the line to get the path
                            found_misuse = line[len("File: "):]
                            found_misuse = normalize_result_misuse_path(found_misuse)

                            print("Comparing found misuse {}".format(found_misuse), file=log)

                            if found_misuse == normed_misuse_file:
                                print("Match found!", file=log)
                                return 1
                            else:
                                print("No match", file=log)
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


def evaluate_results():
    """
    For every data files checks if the result of the misuse detection found the misuse and writes the results to a file
    :rtype: list
    :return: A tuple of the form: (number of data files, number of finished misuse detections, number of found misuses)
    """
    try:
        results = datareader.on_all_data_do(evaluate_single_result)

        def to_data_name(result): return result[0]
        def to_success(result): return result[1]

        applied_results = [result for result in results if result[1] is not None]

        total = len(results)
        applied = len(applied_results)
        found = sum(map(to_success, applied_results))

        def was_successful(result): return result[1] is 1
        def was_not_successful(result): return result[1] is 0
        def finished_with_error(result): return result[1] is None

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
            print('These cases encountered an error (see logs for more information):', file=file_result)
            print('\n'.join(misuses_with_errors), file=file_result)
            print('----------------------------------------------', file=file_result)

        return total, applied, found
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        exception_string = traceback.format_exc()
        print(exception_string)
        log_error(exception_string)


def normalize_data_misuse_path(misuse_file: str):
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


def normalize_result_misuse_path(misuse_file: str):
    """
    Normalizes the misuse file path (from a result file)
    :param misuse_file: The path that is given in the result file
    :rtype: str
    :return: The normalized path (can be compared to normalized data paths)
    """
    normed_misuse_file = normpath(misuse_file)

    # cut everything before project subfolder
    if settings.TEMP_SUBFOLDER + os.sep in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(settings.TEMP_SUBFOLDER + os.sep, 1)[1]

    # cut project subfolder
    if os.sep in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(os.sep, 1)[1]

    # cut trunk folder (only for svn repositories)
    if 'trunk' + os.sep in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split('trunk' + os.sep, 1)[1]

    return normed_misuse_file
