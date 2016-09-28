from enum import Enum
from genericpath import exists
from os import makedirs
from os.path import join
from typing import Dict
from typing import List
from typing import Optional

import yaml

from benchmark.data.detector import Detector
from benchmark.data.finding import Finding
from benchmark.data.misuse import Misuse
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import read_yaml, write_yaml, remove_tree


class Run:
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    def __init__(self, detector: Detector, findings_path: str, version: ProjectVersion):
        self.detector = detector
        self.__findings_base_path = findings_path
        self.findings_path = join(findings_path, version.project_id, version.version_id)
        self.version = version

        self.findings_file_path = join(self.findings_path, Run.FINDINGS_FILE)
        self.run_file_path = join(self.findings_path, Run.RUN_FILE)

        self.result = None  # type: Result
        self.runtime = None  # type: float
        self.detector_md5 = None  # type: Optional[str]
        self.message = ""
        self.__FINDINGS = []  # type: List[Finding]
        if exists(self.run_file_path):
            data = read_yaml(self.run_file_path)
            self.result = Result[data["result"]]
            self.runtime = data.get("runtime", -1)
            self.detector_md5 = data.get("md5", None)
            self.message = data.get("message", "")

    def is_success(self):
        return self.result == Result.success

    def is_error(self):
        return self.result == Result.error

    def is_timeout(self):
        return self.result == Result.timeout

    def is_failure(self):
        return self.is_error() or self.is_timeout()

    @property
    def findings(self) -> List[Finding]:
        if not self.__FINDINGS:
            if exists(self.findings_file_path):
                with open(self.findings_file_path, "r") as stream:
                    self.__FINDINGS = [Finding(data) for data in yaml.load_all(stream) if data]
        return self.__FINDINGS

    def get_potential_hits(self, misuse: Misuse):
        potential_hits = self.__get_potential_hits(misuse, False)
        if not potential_hits:
            potential_hits = self.__get_potential_hits(misuse, True)
        return potential_hits

    def __get_potential_hits(self, misuse: Misuse, method_name_only: bool):
        potential_hits = []
        for finding in self.findings:
            if finding.is_potential_hit(misuse, method_name_only):
                potential_hits.append(finding)
        return potential_hits

    def save(self, detector_md5: str):
        run_data = read_yaml(self.run_file_path) if exists(self.run_file_path) else {}
        run_data.update(
            {"result": self.result.name, "runtime": self.runtime, "message": self.message, "md5": detector_md5})
        write_yaml(run_data, file=self.run_file_path)

    def reset(self):
        remove_tree(self.findings_path)
        makedirs(self.findings_path, exist_ok=True)
        self.__init__(self.detector, self.__findings_base_path, self.version)

    def __str__(self):
        return "run on {}".format(self.version)


class Result(Enum):
    error = 0
    success = 1
    timeout = 2
