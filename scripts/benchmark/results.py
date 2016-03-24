from genericpath import isdir, exists
from os import listdir
from os.path import join, splitext
from os.path import normpath, basename

import datareader
import settings
from utils.io import safe_open, safe_write


def evaluate_single_result(file_data, data_content):
    def evaluate():
        with safe_open(settings.LOG_FILE_RESULTS_EVALUATION, 'a+') as log:
            file_result = join(dir_result, settings.FILE_DETECTOR_RESULT)
            print("===========================================================", file=log)
            print("Evaluating result {} against data {}".format(file_result, file_data), file=log)

            fix_filename = data_content["fix"]["files"][0]["name"]
            fix_filename = normpath(fix_filename)
            if "trunk" in fix_filename:
                # cut everything including trunk folder, then use [1:] to cut the leading slash
                fix_filename = fix_filename.split("trunk", 1)[1][1:]

            print("Looking for file {}".format(fix_filename), file=log)

            if exists(file_result):
                lines = [line.rstrip('\n') for line in safe_open(file_result, 'r')]

                for line in lines:
                    if line.startswith("File: "):
                        found_misuse = line[len("File: "):]
                        found_misuse = normpath(found_misuse)
                        # cut everything including the temp folder, then use [1:] to cut the leading slash
                        split = found_misuse.split(settings.TEMP_SUBFOLDER, 1)
                        if len(split) > 1:
                            found_misuse = split[1][1:]

                        print("Comparing found misuse {}".format(found_misuse), file=log)

                        if found_misuse == fix_filename:
                            print("Match found!", file=log)
                            return 1
            print("No match", file=log)
            return 0

    dirs_results = [join(settings.RESULTS_PATH, result_dir) for result_dir in listdir(settings.RESULTS_PATH) if
                    isdir(join(settings.RESULTS_PATH, result_dir))]
    for dir_result in dirs_results:
        is_result_for_file = splitext(basename(normpath(file_data)))[0] == basename(normpath(dir_result))
        if is_result_for_file:
            return evaluate()
    return None  # to indicate that no result was found for this data


def evaluate_results():
    results = datareader.on_all_data_do(evaluate_single_result)
    applied_results = [result for result in results if result is not None]

    total = len(results)
    applied = len(applied_results)
    found = sum(applied_results)

    with safe_open(settings.BENCHMARK_RESULT_FILE, 'a+') as file_result:
        print('Total number of misuses in the benchmark: ' + str(total), file=file_result)
        print('Number of analyzed misuses (might be less due to ignore or errors): ' + str(applied), file=file_result)
        print('Number of misuses found: ' + str(found), file=file_result)

    return total, applied, found
