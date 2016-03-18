from os import listdir
from os.path import isfile, join

import yaml
from settings import *


def on_all_data_do(function):
    """
    :param function: The function to execute on each data point
    :rtype: list
    :return: A list of the results of each function execution
    """

    datafiles = [join(DATA_PATH, file) for file in listdir(DATA_PATH) if
                 isfile(join(DATA_PATH, file)) and file.endswith(".yml")]

    result = []
    for i, file in enumerate(datafiles, start=1):
        stream = open(file, 'r')

        if VERBOSE:
            print("({}/{}) files: now on {}".format(i, len(datafiles), file))

        try:
            yaml_content = yaml.load(stream)
            result.append(function(file, yaml_content))
        finally:
            stream.close()
            if VERBOSE:
                print("------------------------------------------------------------")

    return result
