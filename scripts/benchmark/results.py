import os
import traceback
from genericpath import isdir, exists
from os import listdir
from os.path import join, splitext
from os.path import normpath, basename

import datareader
import settings
from utils.io import safe_open
from utils.logger import log_error


def evaluate_single_result(file_data: str, data_content: dict):
    """
    Evaluates the result for the given misuse data
    :param file_data: The file containing the misuse data
    :param data_content: The dictionary containing the misuse data
    :return: 1 iff the detector found the misuse; 0 iff it did not find the misuse; None if an error was logged
    """

    def evaluate():
        """
        Returns 1 iff the detector found the misuse; else returns 0
        :rtype: int
        """
        with safe_open(settings.LOG_FILE_RESULTS_EVALUATION, 'a+') as log:
            print("===========================================================", file=log)

            if exists(join(dir_result, settings.FILE_IGNORED)):
                print("{} was ignored by the benchmark".format(file_data), file=log)
                return

            file_result = join(dir_result, settings.FILE_DETECTOR_RESULT)
            print("Evaluating result {} against data {}".format(file_result, file_data), file=log)

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
        is_result_for_file = splitext(basename(normpath(file_data)))[0] == basename(normpath(dir_result))
        if is_result_for_file:
            return evaluate()
    return None


def evaluate_results():
    """
    For every data files checks if the result of the misuse detection found the misuse
    :rtype: list
    :return: A triple of the form (number of data files, number of finished misuse detections, number of found misuses)
    """
    try:
        results = datareader.on_all_data_do(evaluate_single_result)
        applied_results = [result for result in results if result is not None]

        total = len(results)
        applied = len(applied_results)
        found = sum(applied_results)

        with safe_open(settings.BENCHMARK_RESULT_FILE, 'a+') as file_result:
            print('Total number of misuses in the benchmark: ' + str(total), file=file_result)
            print('Number of analyzed misuses (might be less due to ignore or errors): ' + str(applied),
                  file=file_result)
            print('Number of misuses found: ' + str(found), file=file_result)

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
