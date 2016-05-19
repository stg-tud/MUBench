import yaml
from os import listdir
from os.path import isfile, join, basename
from typing import List, Any, Callable


class DataReader:
    def __init__(self, data_path: str, white_list: List[str], black_list: List[str]):
        self.functions = []

        self.data_path = data_path
        self.white_list = white_list
        self.black_list = black_list

    def add(self, function: Callable):
        self.functions.append(function)

    def run(self) -> List[Any]:

        datafiles = [join(self.data_path, file) for file in listdir(self.data_path) if
                     isfile(join(self.data_path, file)) and file.endswith(".yml")]

        result = []
        for i, file in enumerate(datafiles, start=1):
            whitelisted = any([white_listed in file for white_listed in self.white_list])
            blacklisted = any([black_listed in file for black_listed in self.black_list])
            if not whitelisted or blacklisted:
                continue

            stream = open(file, 'r')

            print("Misuse '{}' ({}/{}) > ".format(basename(file), i, len(datafiles)), flush=True)

            try:
                yaml_content = yaml.load(stream)
                for function in self.functions:
                    try:
                        function_out = function(file, yaml_content)
                        if function_out is not None:
                            result.append(function_out)
                    except Continue:
                        break
            finally:
                stream.close()

        return result


class Continue(Exception):
    def __init__(self):
        super(Continue, self).__init__()
