from enum import Enum
from genericpath import exists
from os.path import join
from typing import Dict
from typing import List
from typing import Optional

import yaml

from benchmark.utils.io import read_yaml, write_yaml, remove_tree


class Run:
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    def __init__(self, path: str):
        self.__path = path
        self.__findings_file_path = join(path, Run.FINDINGS_FILE)
        self.__run_file_path = join(path, Run.RUN_FILE)
        self.result = None  # type: Result
        self.runtime = None  # type: float
        self.detector_md5 = None  # type: Optional[str]
        self.message = ""
        self.__findings = []  # type: List[Dict[str,str]]
        if exists(self.__run_file_path):
            data = read_yaml(self.__run_file_path)
            self.result = Result[data["result"]]
            self.runtime = data.get("runtime", -1)
            self.detector_md5 = data.get("md5", None)
            self.message = data.get("message", "")

    def is_success(self):
        return self.result == Result.success

    def is_failure(self):
        return self.result == Result.error or self.result == Result.timeout

    @property
    def findings(self):
        if not self.__findings:
            if exists(self.__findings_file_path):
                with open(self.__findings_file_path, "r") as stream:
                    self.__findings = [finding for finding in yaml.load_all(stream) if finding]
        return self.__findings

    def write(self, detector_md5: str):
        run_data = read_yaml(self.__run_file_path) if exists(self.__run_file_path) else {}
        run_data.update(
            {"result": self.result.name, "runtime": self.runtime, "message": self.message, "md5": detector_md5})
        write_yaml(run_data, file=self.__run_file_path)

    def reset(self):
        path = self.__path
        remove_tree(path)
        self.__init__(path)


class Result(Enum):
    error = 0
    success = 1
    timeout = 2
