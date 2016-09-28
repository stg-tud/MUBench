from enum import Enum, IntEnum
from genericpath import exists
from logging import Logger
from os import makedirs
from os.path import join
from typing import List
from typing import Optional

import yaml

from benchmark.data.detector import Detector
from benchmark.data.finding import Finding
from benchmark.data.misuse import Misuse
from benchmark.data.project_compile import ProjectCompile
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import read_yaml, write_yaml, remove_tree
from benchmark.utils.shell import Shell


class DetectorMode(IntEnum):
    mine_and_detect = 0
    detect_only = 1


class Result(Enum):
    error = 0
    success = 1
    timeout = 2


def _quote(value: str):
    return "\"{}\"".format(value)


class Run:
    def __init__(self, detector: Detector, version: ProjectVersion):
        self.detector = detector
        self.version = version

        self._detector_md5 = "-invalid-"

        self.__FINDINGS = []

    def execute(self, compiles_path: str, timeout: Optional[int], logger: Logger):
        raise NotImplementedError()

    def is_success(self):
        raise NotImplementedError()

    def is_error(self):
        raise NotImplementedError()

    def is_timeout(self):
        raise NotImplementedError()

    def is_failure(self):
        return self.is_error() or self.is_timeout()

    def is_outdated(self):
        return self.detector.md5 != self._detector_md5

    @property
    def findings(self) -> List[Finding]:
        if not self.__FINDINGS:
            self.__FINDINGS = self._load_findings()
        return self.__FINDINGS

    def _load_findings(self) -> List[Finding]:
        raise NotImplementedError()

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

    def save(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()


class VersionRun(Run):
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    key_findings_file = "target"
    key_run_file = "run_info"
    key_detector_mode = "detector_mode"
    key_training_src_path = "training_src_path"
    key_training_classpath = "training_classpath"
    key_target_src_path = "target_src_path"
    key_target_classpath = "target_classpath"

    def __init__(self, detector: Detector, findings_path: str, version: ProjectVersion):
        super().__init__(detector, version)
        self.__findings_base_path = findings_path
        self.__load()

    def _get_findings_path(self):
        return join(self.__findings_base_path,
                    self._get_run_mode().name, self.detector.id,
                    self.version.project_id, self.version.version_id)

    def _get_run_mode(self):
        return DetectorMode.mine_and_detect

    @property
    def _run_file_path(self):
        return join(self._get_findings_path(), self.RUN_FILE)

    def __load(self):
        data = self.__load_data(self._run_file_path)
        self.result = Result[data["result"]] if data["result"] else None
        self.runtime = data["runtime"]
        self.message = data["message"]
        self._detector_md5 = data["md5"]

    @staticmethod
    def __load_data(run_file_path: str):
        data = {
            "result": None,
            "runtime": None,
            "message": "",
            "md5": None
        }
        data.update(read_yaml(run_file_path) if exists(run_file_path) else {})
        return data

    def _load_findings(self):
        if exists(self._findings_file_path):
            with open(self._findings_file_path, "r") as stream:
                return [Finding(data) for data in yaml.load_all(stream) if data]
        else:
            return []

    @property
    def _findings_file_path(self):
        return join(self._get_findings_path(), self.FINDINGS_FILE)

    def is_success(self):
        return self.result == Result.success

    def is_error(self):
        return self.result == Result.error

    def is_timeout(self):
        return self.result == Result.timeout

    def execute(self, compiles_path: str, timeout: Optional[int], logger: Logger):
        detector_invocation = ["java"] + self.detector.java_options + ["-jar", _quote(self.detector.jar_path)]
        command = detector_invocation + self._get_detector_arguments(self.version.get_compile(compiles_path))
        command = " ".join(command)
        return Shell.exec(command, logger=logger, timeout=timeout)

    def _get_detector_arguments(self, project_compile: ProjectCompile) -> List[str]:
        return [
            self.key_findings_file, _quote(self._findings_file_path),
            self.key_run_file, _quote(self._run_file_path),
            self.key_detector_mode, _quote(self._run_mode_detector_argument),
            self.key_target_src_path, _quote(project_compile.original_sources_path),
            self.key_target_classpath, _quote(project_compile.original_classes_path)
        ]

    @property
    def _run_mode_detector_argument(self):
        return str(int(self._get_run_mode()))

    def save(self):
        # load and update, since an execution might have written additional fields to the file since initialization
        run_data = self.__load_data(self._run_file_path)
        run_data.update({
            "result": self.result.name,
            "runtime": self.runtime,
            "message": self.message,
            "md5": self.detector.md5
        })
        write_yaml(run_data, file=self._run_file_path)

    def reset(self):
        remove_tree(self._get_findings_path())
        makedirs(self._get_findings_path(), exist_ok=True)
        self.__load()

    def __str__(self):
        return "run on {}".format(self.version)


class MisuseWithPatternRun(VersionRun):
    def __init__(self, detector: Detector, findings_path: str, version: ProjectVersion, misuse: Misuse):
        self.misuse = misuse
        super().__init__(detector, findings_path, version)

    def _get_run_mode(self):
        return DetectorMode.detect_only

    def _get_findings_path(self):
        return join(super()._get_findings_path(), self.misuse.misuse_id)

    def _get_detector_arguments(self, project_compile: ProjectCompile):
        return [
            self.key_findings_file, _quote(self._findings_file_path),
            self.key_run_file, _quote(self._run_file_path),
            self.key_detector_mode, _quote(self._run_mode_detector_argument),
            self.key_training_src_path, _quote(project_compile.get_pattern_source_path(self.misuse)),
            self.key_training_classpath, _quote(project_compile.get_pattern_classes_path(self.misuse)),
            self.key_target_src_path, _quote(project_compile.misuse_source_path),
            self.key_target_classpath, _quote(project_compile.misuse_classes_path)
        ]


class PerMisuseRun(VersionRun):
    def __init__(self, detector: Detector, findings_path: str, version: ProjectVersion):
        super().__init__(detector, findings_path, version)

        misuses = version.misuses
        if not misuses:
            raise ValueError("no misuses to run on")
        else:
            self.__misuse_runs = [MisuseWithPatternRun(detector, findings_path, version, misuse) for misuse in misuses]
            # noinspection PyProtectedMember
            self._detector_md5 = self.__misuse_runs[0]._detector_md5

    def _get_run_mode(self):
        return DetectorMode.detect_only

    def _load_findings(self) -> List[Finding]:
        return [finding for misuse_run in self.__misuse_runs for finding in misuse_run.findings]

    def execute(self, compiles_path: str, timeout: Optional[int], logger: Logger):
        for run in self.__misuse_runs:
            run.execute(compiles_path, timeout, logger)

    def reset(self):
        super().reset()
        for run in self.__misuse_runs:
            run.reset()
