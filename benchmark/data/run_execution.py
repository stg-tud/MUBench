from enum import Enum, IntEnum
from logging import Logger
from os import makedirs
from os.path import join, exists

import yaml
from typing import Optional, List

from benchmark.data.detector import Detector
from benchmark.data.finding import Finding
from benchmark.data.misuse import Misuse
from benchmark.data.project_compile import ProjectCompile
from benchmark.data.project_version import ProjectVersion
from benchmark.data.findings_filters import FindingsFilter
from benchmark.utils.io import write_yaml, remove_tree, read_yaml
from benchmark.utils.shell import Shell


def _quote(value: str):
    return "\"{}\"".format(value)


class Result(Enum):
    error = 0
    success = 1
    timeout = 2


class DetectorMode(IntEnum):
    mine_and_detect = 0
    detect_only = 1


class RunExecutionState:
    def __init__(self, detector: Detector, run_file: str):
        self.detector = detector
        self.run_file = run_file

        data = {
            "result": None,
            "runtime": None,
            "message": "",
            "md5": None
        }
        data.update(read_yaml(run_file) if exists(run_file) else {})
        self.execution_result = Result[data["result"]] if data["result"] else None
        self.runtime = data["runtime"]
        self.message = data["message"]
        self._detector_md5 = data["md5"]

    def is_success(self):
        return self.execution_result == Result.success

    def is_error(self):
        return self.execution_result == Result.error

    def is_timeout(self):
        return self.execution_result == Result.timeout

    def is_failure(self):
        return self.is_error() or self.is_timeout()

    def is_outdated(self):
        return self.detector.md5 != self._detector_md5

    def save(self):
        # load and update, since an execution might have written additional fields to the file since initialization
        run_data = self.__load_data(self.run_file)
        run_data.update({
            "result": self.execution_result.name if self.execution_result else None,
            "runtime": self.runtime,
            "message": self.message,
            "md5": self.detector.md5
        })
        write_yaml(run_data, file=self.run_file)

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


class RunExecution:
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    key_findings_file = "target"
    key_run_file = "run_info"
    key_detector_mode = "detector_mode"
    key_training_src_path = "training_src_path"
    key_training_classpath = "training_classpath"
    key_target_src_path = "target_src_path"
    key_target_classpath = "target_classpath"

    def __init__(self, run_mode: DetectorMode, detector: Detector, version: ProjectVersion, findings_base_path: str,
                 findings_filter: FindingsFilter):
        self.run_mode = run_mode
        self.detector = detector
        self.version = version
        self._findings_base_path = findings_base_path
        self._findings_file_path = join(self._get_findings_path(), self.FINDINGS_FILE)
        self.__FINDINGS = None

        self.findings_filter = findings_filter

    def execute(self, compile_base_path: str, timeout: Optional[int], logger: Logger):
        detector_invocation = ["java"] + self.detector.java_options + ["-jar", _quote(self.detector.jar_path)]
        command = detector_invocation + self._get_detector_arguments(self.version.get_compile(compile_base_path))
        command = " ".join(command)
        return Shell.exec(command, logger=logger, timeout=timeout)

    @property
    def potential_hits(self):
        return self.findings_filter.get_potential_hits(self.findings, self._get_findings_path())

    @property
    def findings(self) -> List[Finding]:
        if not self.__FINDINGS:
            self.__FINDINGS = self._load_findings()
        return self.__FINDINGS

    @property
    def _run_file_path(self):
        return join(self._get_findings_path(), self.RUN_FILE)

    @property
    def _run_mode_detector_argument(self):
        return str(int(self.run_mode))

    def _get_findings_path(self):
        raise NotImplementedError

    def _get_detector_arguments(self, project_compile: ProjectCompile):
        raise NotImplementedError

    def _load_findings(self):
        raise NotImplementedError

    @property
    def state(self):
        return RunExecutionState(self.detector, self._run_file_path)

    def save(self):
        self.state.save()

    def reset(self):
        remove_tree(self._get_findings_path())
        makedirs(self._get_findings_path(), exist_ok=True)
        RunExecution.__init__(self, self.run_mode, self.detector, self.version, self._findings_base_path,
                              self.findings_filter)

    def __str__(self):
        return str(self.version)


class VersionExecution(RunExecution):
    def __init__(self, run_mode: DetectorMode, detector: Detector, version: ProjectVersion, findings_base_path: str,
                 findings_filter: FindingsFilter):
        super().__init__(run_mode, detector, version, findings_base_path, findings_filter)

    def _get_findings_path(self):
        return join(self._findings_base_path,
                    self.run_mode.name, self.detector.id,
                    self.version.project_id, self.version.version_id)

    def _get_detector_arguments(self, project_compile: ProjectCompile):
        return [
            self.key_findings_file, _quote(self._findings_file_path),
            self.key_run_file, _quote(self._run_file_path),
            self.key_detector_mode, _quote(self._run_mode_detector_argument),
            self.key_target_src_path, _quote(project_compile.original_sources_path),
            self.key_target_classpath, _quote(project_compile.original_classes_path)
        ]

    def _load_findings(self):
        if exists(self._findings_file_path):
            with open(self._findings_file_path) as stream:
                return [Finding(data) for data in yaml.load_all(stream) if data]
        else:
            return []


class MisuseExecution(RunExecution):
    def __init__(self, run_mode: DetectorMode, detector: Detector, version: ProjectVersion, misuse: Misuse,
                 findings_base_path: str, findings_filter: FindingsFilter):
        self.misuse = misuse
        super().__init__(run_mode, detector, version, findings_base_path, findings_filter)

    def _get_findings_path(self):
        return join(self._findings_base_path,
                    self.run_mode.name, self.detector.id,
                    self.version.project_id, self.version.version_id, self.misuse.misuse_id)

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

    def _load_findings(self):
        if exists(self._findings_file_path):
            with open(self._findings_file_path) as stream:
                return [Finding(data) for data in yaml.load_all(stream) if data]
        else:
            return []
