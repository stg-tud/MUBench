from os import listdir
from os.path import isfile, join, basename

import yaml
from typing import List, Callable, Dict, TypeVar, Union

T = TypeVar('ResultType')


def on_all_data_do(data_path: str,
                   function: Callable[[str, Dict[str, Union[str, Dict]]], T],
                   white_list: List[str],
                   black_list: List[str]) -> List[T]:

    datafiles = [join(data_path, file) for file in listdir(data_path) if
                 isfile(join(data_path, file)) and file.endswith(".yml")]

    result = []
    for i, file in enumerate(datafiles, start=1):
        whitelisted = any([white_listed in file for white_listed in white_list])
        blacklisted = any([black_listed in file for black_listed in black_list])
        if not whitelisted or blacklisted:
            print("({}/{}) {} : ignored".format(i, len(datafiles), basename(file)))
            continue

        stream = open(file, 'r')

        print("({}/{}) {} : ".format(i, len(datafiles), basename(file)))

        try:
            yaml_content = yaml.load(stream)
            result.append(function(file, yaml_content))
        finally:
            stream.close()

    return result
