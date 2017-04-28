import time
import yaml
from enum import Enum, IntEnum
from logging import Logger
from os import makedirs
from os.path import join, exists
from typing import Optional, List, Dict

from data.detector import Detector
from data.finding import Finding
from data.findings_filters import FindingsFilter
from data.misuse import Misuse
from data.project_compile import ProjectCompile
from data.project_version import ProjectVersion
from utils.io import write_yaml, remove_tree, read_yaml
from utils.shell import Shell, CommandFailedError


def _quote(value: str):
    return "\"{}\"".format(value)


class Result(Enum):
    error = 0
    success = 1
    timeout = 2


class DetectorMode(IntEnum):
    mine_and_detect = 0
    detect_only = 1


class DetectorExecution:
    RUN_FILE = "run.yml"
    FINDINGS_FILE = "findings.yml"

    key_findings_file = "target"
    key_run_file = "run_info"
    key_detector_mode = "detector_mode"
    key_training_src_path = "training_src_path"
    key_training_classpath = "training_classpath"
    key_target_src_path = "target_src_path"
    key_target_classpath = "target_classpath"
    key_dependency_classpath = "dep_classpath"

    def __init__(self, run_mode: DetectorMode, detector: Detector, version: ProjectVersion, findings_base_path: str,
                 findings_filter: FindingsFilter):
        self.run_mode = run_mode
        self.detector = detector
        self.version = version
        self._findings_base_path = findings_base_path
        self._findings_file_path = join(self._get_findings_path(), self.FINDINGS_FILE)
        self.__FINDINGS = None
        self.__POTENTIAL_HITS = None

        data = {
            "result": None,
            "runtime": 0,
            "message": "",
            "md5": None
        }
        data.update(read_yaml(self._run_file_path) if exists(self._run_file_path) else {})
        self.result = Result[data["result"]] if data["result"] else None
        self.runtime = data["runtime"]
        self.message = data["message"]
        self._detector_md5 = data["md5"]

        self.findings_filter = findings_filter

    def execute(self, compile_base_path: str, timeout: Optional[int], logger: Logger):
        detector_invocation = ["java"] + self.detector.java_options + ["-jar", _quote(self.detector.jar_path)]
        command = detector_invocation + self._get_detector_arguments(self.version.get_compile(compile_base_path))
        command = " ".join(command)

        start = time.time()
        try:
            Shell.exec(command, logger=logger, timeout=timeout)
            self.result = Result.success
        except CommandFailedError as e:
            logger.error("Detector failed: %s", e)
            self.result = Result.error
            message = str(e)
            message_lines = str.splitlines(message)
            if len(message_lines) > 5000:
                self.message = "\n".join(message_lines[0:500]) + "\n" + "\n".join(message_lines[-4500:])
            else:
                self.message = message
        except TimeoutError:
            logger.error("Detector took longer than the maximum of %s seconds", timeout)
            self.result = Result.timeout
        finally:
            end = time.time()
            runtime = end - start
            self.runtime = runtime
            logger.info("Run took {0:.2f} seconds.".format(runtime))

        self.save()

    @property
    def potential_hits(self):
        if not self.__POTENTIAL_HITS:
            potential_hits = self.findings_filter.get_potential_hits(self.__findings)
            self.__POTENTIAL_HITS = self.detector.specialize_findings(self._get_findings_path(), potential_hits)
        return self.__POTENTIAL_HITS

    @property
    def __findings(self) -> List[Finding]:
        if not self.__FINDINGS:
            self.__FINDINGS = self._load_findings()
        return self.__FINDINGS

    @property
    def number_of_findings(self):
        return len(self.__findings)

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
        if exists(self._findings_file_path):
            with open(self._findings_file_path, 'rU', encoding="utf-8") as stream:
                return [self.__create_finding(data) for data in (yaml.load_all(stream)) if data]
        else:
            return []

    @staticmethod
    def __create_finding(data: Dict):
        data["rank"] = data.pop("id")
        return Finding(data)

    def save(self):
        # load and update, since an execution might have written additional fields to the file since initialization
        run_data = self.__load_data(self._run_file_path)
        run_data.update({
            "result": self.result.name if self.result else None,
            "runtime": self.runtime,
            "message": self.message,
            "md5": self.detector.md5
        })
        write_yaml(run_data, file=self._run_file_path)

    def reset(self):
        remove_tree(self._get_findings_path())
        makedirs(self._get_findings_path(), exist_ok=True)
        DetectorExecution.__init__(self, self.run_mode, self.detector, self.version, self._findings_base_path,
                                   self.findings_filter)

    def is_success(self):
        return self.result == Result.success

    def is_error(self):
        return self.result == Result.error

    def is_timeout(self):
        return self.result == Result.timeout

    def is_failure(self):
        return self.is_error() or self.is_timeout()

    def is_outdated(self):
        return self.detector.md5 != self._detector_md5

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

    def __str__(self):
        return str(self.version)


class MineAndDetectExecution(DetectorExecution):
    def __init__(self, detector: Detector, version: ProjectVersion, findings_base_path: str,
                 findings_filter: FindingsFilter):
        super().__init__(DetectorMode.mine_and_detect, detector, version, findings_base_path, findings_filter)

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
            self.key_target_classpath, _quote(project_compile.original_classes_path),
            self.key_dependency_classpath, _quote(project_compile.get_dependency_classpath())
        ]


class DetectOnlyExecution(DetectorExecution):
    def __init__(self, detector: Detector, version: ProjectVersion, misuse: Misuse, findings_base_path: str,
                 findings_filter: FindingsFilter):
        self.misuse = misuse
        super().__init__(DetectorMode.detect_only, detector, version, findings_base_path, findings_filter)

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
            self.key_target_classpath, _quote(project_compile.misuse_classes_path),
            self.key_dependency_classpath, _quote(self.__get_dependency_classpath(project_compile))
        ]

    @staticmethod
    def __get_dependency_classpath(project_compile):
        dependency_classpath = project_compile.get_dependency_classpath()
        if dependency_classpath:
            return project_compile.original_classpath + ":" + dependency_classpath
        else:
            return project_compile.original_classpath
