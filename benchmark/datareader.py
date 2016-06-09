from enum import Enum
from os import listdir
from os.path import join

from typing import List, Callable

from benchmark.misuse import Misuse


class DataReader:
    def __init__(self, data_path: str, white_list: List[str], black_list: List[str]):
        self.functions = []
        self.data_path = data_path
        self.white_list = white_list
        self.black_list = black_list

    def add(self, function: Callable):
        self.functions.append(function)

    def run(self) -> None:
        misuses = self._get_misuses()

        for i, misuse in enumerate(misuses, start=1):
            print("Misuse '{}' ({}/{}) > ".format(misuse, i, len(misuses)), flush=True)

            for function in self.functions:
                function_out = function(misuse)
                if function_out is DataReader.Result.skip:
                    continue
                if function_out is DataReader.Result.exit:
                    break

    def _get_misuses(self):
        candidates = [join(self.data_path, file) for file in sorted(listdir(self.data_path))]
        misuses = [Misuse(path) for path in candidates if Misuse.ismisuse(path)]
        misuses = [misuse for misuse in misuses if not self.__skip(misuse.name)]
        return misuses

    def __skip(self, file: str):
        whitelisted = any([white_listed in file for white_listed in self.white_list])
        blacklisted = any([black_listed in file for black_listed in self.black_list])
        return not whitelisted or blacklisted

    class Result(Enum):
        ok = 0
        skip = 1
        exit = 2
