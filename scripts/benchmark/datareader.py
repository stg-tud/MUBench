from os import listdir
from os.path import isfile, join

import yaml


def on_all_data_do(function, data_path, verbose):
    datafiles = [join(data_path, file) for file in listdir(data_path) if
                 isfile(join(data_path, file)) and file.endswith(".yml")]

    result = []
    for i, file in enumerate(datafiles, start=1):
        stream = open(file, 'r')

        if verbose:
            print("({}/{}) files: now on {}".format(i, len(datafiles), file))

        try:
            yaml_content = yaml.load(stream)
            result.append(function(file, yaml_content))
        finally:
            stream.close()
            if verbose:
                print("------------------------------------------------------------")

    return result

# example usage:
# from pprint import pprint
#
# def f(file, data):
#    return "({} -> {})".format(file, data)
#
# data_path = r'<path>\MUBench\data'
# results = on_all_data_do(f, data_path, True)
# pprint(results)
