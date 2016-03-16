from genericpath import isdir
from os import listdir
from os.path import join, splitext
from os.path import normpath, basename

import datareader
from settings import *


def evaluate_single_result(file_data, data_content):
    # TODO: Re-implement this for other outputs
    def evaluate():
        file_result = join(dir_result, FILE_DETECTOR_RESULT)
        print("Evaluating result {} against data {}".format(file_result, file_data))

        lines = [line.rstrip('\n') for line in open(file_result)]

        for line in lines:
            if line.startswith("File: "):
                found_misuse = line.split(' ', 1)[1]

                if TEMP_SUBFOLDER + '\\' in found_misuse:
                    found_misuse = found_misuse.split(TEMP_SUBFOLDER + '\\', 1)[1]

                fix_filename = data_content["fix"]["files"][0]["name"]
                print(fix_filename)
                if 'trunk/' in fix_filename:
                    fix_filename = fix_filename.split('trunk/', 1)[1]

                print("Comparing fixed file {} against file with misuse found {}".format(fix_filename, found_misuse))
                if normpath(found_misuse) == normpath(fix_filename):
                    return 1

        return 0

    dirs_results = [join(RESULTS_PATH, result_dir) for result_dir in listdir(RESULTS_PATH) if
                    isdir(join(RESULTS_PATH, result_dir))]
    for dir_result in dirs_results:
        is_result_for_file = splitext(basename(normpath(file_data)))[0] == basename(normpath(dir_result))
        if is_result_for_file:
            return evaluate()
    return None # to indicate that no result was found for this data


def evaluate_results():
    results = [result for result in datareader.on_all_data_do(evaluate_single_result) if
               result is not None]
    write_results(results)


def write_results(results):
    count_success = sum(results)
    count_data = len(results)

    benchmark_result = "Found {} of {} misuses!".format(count_success, count_data)
    print(benchmark_result)
    print(benchmark_result, file=open(FILE_BENCHMARK_RESULT, 'w+'))
    return benchmark_result
