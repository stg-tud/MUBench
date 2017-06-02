import time
from enum import Enum, IntEnum
from logging import Logger
from os import makedirs
from os.path import join

from typing import Optional, List, Dict

from data.detector import Detector
from data.finding import Finding
from data.findings_filters import FindingsFilter
from data.misuse import Misuse
from data.project_compile import ProjectCompile
from data.project_version import ProjectVersion
from data.runner_interface import NoCompatibleRunnerInterface
from utils.io import write_yaml, remove_tree, read_yaml_if_exists, open_yamls_if_exists
from utils.shell import Shell, CommandFailedError


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
        self._findings_filter = findings_filter
        self._findings_base_path = findings_base_path
        self.__FINDINGS = None
        self.__POTENTIAL_HITS = None
        self.__run_info = None

    def __get_run_info(self, key: str, default):
        if not self.__run_info:
            self.__run_info = self.__load_run_info()
        return self.__run_info.get(key, default)

    def __load_run_info(self):
        return read_yaml_if_exists(self._run_file_path)

    @property
    def result(self):
        result = self.__get_run_info("result", None)
        return Result[result] if result else None

    @property
    def runtime(self):
        return self.__get_run_info("runtime", None)

    @property
    def message(self):
        return self.__get_run_info("message", "")

    @property
    def __detector_md5(self):
        return self.__get_run_info("md5", None)

    def execute(self, compile_base_path: str, timeout: Optional[int], logger: Logger):
        detector_args = self._get_detector_arguments(self.version.get_compile(compile_base_path))

        start = time.time()
        message = ""
        try:
            self.detector.execute(self.version, detector_args, timeout, logger)
            result = Result.success
        except NoCompatibleRunnerInterface as e:
            logger.error("Cannot run detector, because it has no compatible runner interface: %s", e)
            return
        except CommandFailedError as e:
            logger.error("Detector failed: %s", e)
            result = Result.error
            message = str(e)
            message_lines = str.splitlines(message)
            if len(message_lines) > 5000:
                message = "\n".join(message_lines[0:500]) + "\n" + "\n".join(message_lines[-4500:])
            else:
                message = message
        except TimeoutError:
            logger.error("Detector took longer than the maximum of %s seconds", timeout)
            result = Result.timeout
        finally:
            end = time.time()
            runtime = end - start
            runtime = runtime
            logger.info("Run took {0:.2f} seconds.".format(runtime))

        self.__save_run_info(result, runtime, message, self.detector.md5)

    def __save_run_info(self, result, runtime, message, detector_md5):
        # load and update, since an execution might have written additional fields to the file since initialization
        run_info = self.__load_run_info()
        run_info.update({
            "result": result.name,
            "runtime": runtime,
            "message": message,
            "md5": detector_md5
        })
        write_yaml(run_info, file=self._run_file_path)
        self.__run_info = run_info

    @property
    def potential_hits(self):
        if not self.__POTENTIAL_HITS:
            potential_hits = self._findings_filter.get_potential_hits(self.__findings)
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
    def _findings_file_path(self):
        return join(self._get_findings_path(), self.FINDINGS_FILE)

    @property
    def _run_mode_detector_argument(self):
        return str(int(self.run_mode))

    def _get_findings_path(self):
        raise NotImplementedError

    def _get_command(self, project_compile: ProjectCompile):
        raise NotImplementedError

    def _load_findings(self):
        with open_yamls_if_exists(self._findings_file_path) as findings:
            return [self.__create_finding(rank, data) for rank, data in enumerate(findings) if data]

    @staticmethod
    def __create_finding(rank: int, finding_data: Dict):
        finding_data["rank"] = rank
        return Finding(finding_data)

    def reset(self):
        remove_tree(self._get_findings_path())
        makedirs(self._get_findings_path(), exist_ok=True)
        DetectorExecution.__init__(self, self.run_mode, self.detector, self.version, self._findings_base_path,
                                   self._findings_filter)

    def is_success(self):
        return self.result == Result.success

    def is_error(self):
        return self.result == Result.error

    def is_timeout(self):
        return self.result == Result.timeout

    def is_failure(self):
        return self.is_error() or self.is_timeout()

    def is_outdated(self):
        return self.detector.md5 != self.__detector_md5

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
        return {
            self.key_findings_file : self._findings_file_path,
            self.key_run_file : self._run_file_path,
            self.key_detector_mode : self._run_mode_detector_argument,
            self.key_target_src_path : project_compile.original_sources_path,
            self.key_target_classpath : project_compile.original_classes_path,
            self.key_dependency_classpath : project_compile.get_full_classpath()
        }


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
        return {
            self.key_findings_file : self._findings_file_path,
            self.key_run_file : self._run_file_path,
            self.key_detector_mode : self._run_mode_detector_argument,
            self.key_training_src_path : project_compile.get_pattern_source_path(self.misuse),
            self.key_training_classpath : project_compile.get_pattern_classes_path(self.misuse),
            self.key_target_src_path : project_compile.misuse_source_path,
            self.key_target_classpath : project_compile.misuse_classes_path,
            self.key_dependency_classpath : project_compile.get_full_classpath()
        }
