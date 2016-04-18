from os import listdir
from os.path import isfile, join
from typing import Any, List, Callable, Dict, TypeVar

import yaml

import settings

T = TypeVar('T')


def on_all_data_do(function: Callable[[str, Dict[str, str]], T]) -> List[T]:
    """
    :param function: The function to execute on each data point; the expected signature is function(file, data)
    :rtype: list
    :return: A list of the results of each function execution
    """

    datafiles = [join(settings.DATA_PATH, file) for file in listdir(settings.DATA_PATH) if
                 isfile(join(settings.DATA_PATH, file)) and file.endswith(".yml")]

    result = []
    for i, file in enumerate(datafiles, start=1):
        stream = open(file, 'r')

        if settings.VERBOSE:
            print("({}/{}) files: now on {}".format(i, len(datafiles), file))

        try:
            yaml_content = yaml.load(stream)
            result.append(function(file, yaml_content))
        finally:
            stream.close()
            if settings.VERBOSE:
                print("------------------------------------------------------------")

    return result
