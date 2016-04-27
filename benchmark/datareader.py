from os import listdir
from os.path import isfile, join
from typing import List, Callable, Dict, TypeVar, Union

import yaml

from config import Config

T = TypeVar('ResultType')


def on_all_data_do(function: Callable[[str, Dict[str, Union[str, Dict]]], T]) -> List[T]:
    """
    :param function: The function to execute on each data point; the expected signature is function(file, data)
    :rtype: list
    :return: A list of the results of each function execution
    """

    datafiles = [join(Config.DATA_PATH, file) for file in listdir(Config.DATA_PATH) if
                 isfile(join(Config.DATA_PATH, file)) and file.endswith(".yml")]

    result = []
    for i, file in enumerate(datafiles, start=1):
        blacklisted = any([black_listed in file for black_listed in Config.BLACK_LIST])
        whitelisted = any([white_listed in file for white_listed in Config.WHITE_LIST])
        if not whitelisted or blacklisted:
            print("Warning: ignored {}".format(file))
            break

        stream = open(file, 'r')

        print("({}/{}) files: now on {}".format(i, len(datafiles), file))

        try:
            yaml_content = yaml.load(stream)
            result.append(function(file, yaml_content))
        finally:
            stream.close()
            print("------------------------------------------------------------")

    return result
