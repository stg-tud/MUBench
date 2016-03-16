import ntpath
from genericpath import isdir
from os import listdir
from os.path import join, splitext

import datareader
from settings import *


def evaluate_results():
    dirs_results = [join(RESULTS_PATH, result_dir) for result_dir in listdir(RESULTS_PATH) if
                    isdir(result_dir)]

    # TODO: Re-implement this for other outputs
    def evaluate(file_result, data_content):
        lines = [line.rstrip('\n') for line in open(file_result)]

        for line in lines:
            if line.startswith("File: "):
                found_misuse = line.split(' ', 1)[1]

                if TEMP_SUBFOLDER + '\\' in found_misuse:
                    found_misuse = found_misuse.split(TEMP_SUBFOLDER + '\\', 1)[1]

                fix_filename = data_content["fix"]["files"][0]
                print(fix_filename)
                fix_filename = fix_filename.split('trunk\\', 1)[1]

                print("Comparing fixed file {} against file with misuse found {}".format(fix_filename, found_misuse))
                if found_misuse == fix_filename:
                    return 1

        return 0

    def evaluate_result_from_file(file_data, data_content):
        for dir_result in dirs_results:
            is_result_for_file = splitext(ntpath.basename(file_data))[0] == ntpath.basename(dir_result)
            if is_result_for_file:
                file_result = join(dir_result, FILE_DETECTOR_RESULT)
                print("Evaluating result {} against data {}".format(file_result, file_data))
                return evaluate(file_result, data_content)
        return None

    results = [result for result in datareader.on_all_data_do(evaluate_result_from_file, DATA_PATH) if
               result is not None]

    count_success = sum(results)
    count_data = len(results)

    benchmark_result = "Found {} of {} misuses!".format(count_success, count_data)
    print(benchmark_result)
    print(benchmark_result, file=FILE_BENCHMARK_RESULT)

evaluate_results()