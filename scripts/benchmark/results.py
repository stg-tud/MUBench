import ntpath
from genericpath import isdir
from os import listdir
from os.path import join, splitext

import datareader

FILE_RESULT = "finalAnomalies.txt"  # result written by the misuse detector


def evaluate_results(data_path, results_path, verbose):
    dirs_results = [join(results_path, result_dir) for result_dir in listdir(results_path) if
                    isdir(result_dir)]

    def evaluate(file_result, data_content):
        lines = [line.rstrip('\n') for line in open('filename')]

        for line in lines:
            if line.startswith("File: "):
                found_misuse = line.split(' ', 1)[1]

                if 'trunk\\' in found_misuse:
                    found_misuse = found_misuse.split('misuse\\', 1)[1]

                fix_filename = data_content["fix"]["files"][0]
                print(fix_filename)
                fix_filename = fix_filename.split('trunk\\', 1)[1]

                print("Comparing fixed file {} againt file with misuse found {}".format(fix_filename, found_misuse))
                if found_misuse == fix_filename:
                    return 1

        return 0

    def evaluate_result_from_file(file_data, content):
        for dir_result in dirs_results:
            is_result_for_file = splitext(ntpath.basename(file_data))[0] == ntpath.basename(dir_result)
            if is_result_for_file:
                file_result = join(dir_result, FILE_RESULT)
                print("Evaluating result {} against data {}".format(file_result, file_data))
                return evaluate(file_result, file_data)
        return None

    results = [result for result in datareader.on_all_data_do(evaluate_result_from_file, data_path, verbose) if
               result is not None]

    count_success = sum(results)
    count_data = len(results)

    print("Found {} of {} misuses!".format(count_success, count_data))
