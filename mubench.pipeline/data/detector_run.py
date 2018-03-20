import time
from enum import Enum
from logging import Logger
from os import makedirs
from os.path import join
from typing import Optional, List, Dict

from data.detector import Detector
from data.finding import Finding
from data.project_version import ProjectVersion
from tasks.configurations.detector_interface_configuration import key_findings_file, key_run_file
from utils.io import write_yaml, remove_tree, read_yaml_if_exists, open_yamls_if_exists
from utils.shell import CommandFailedError


class Result(Enum):
    error = 0
    success = 1
    timeout = 2


class DetectorRun:
    __FINDINGS_FILE = "findings.yml"
    __RUN_FILE = "run.yml"

    def __init__(self, detector: Detector, version: ProjectVersion, findings_path: str):
        self.detector = detector
        self.version = version
        self.findings_path = findings_path
        self.__FINDINGS = None
        self.__POTENTIAL_HITS = None
        self.__RUN_INFO = None
        self._findings_file_path = join(findings_path, DetectorRun.__FINDINGS_FILE)
        self._run_file_path = join(findings_path, DetectorRun.__RUN_FILE)

    @property
    def __run_info(self):
        if not self.__RUN_INFO:
            self.__RUN_INFO = self.__load_run_info()
        return self.__RUN_INFO

    def __load_run_info(self):
        return read_yaml_if_exists(self._run_file_path)

    @property
    def result(self):
        result = self.__run_info.get("result", None)
        return Result[result] if result else None

    @property
    def runtime(self):
        return self.__run_info.get("runtime", 0)

    @property
    def message(self):
        return self.__run_info.get("message", "")

    @property
    def __detector_md5(self):
        return self.__run_info.get("md5", None)

    @property
    def __timestamp(self):
        return self.__run_info.get("timestamp", 0)

    def get_run_info(self):
        run_info = {
            "number_of_findings": self.number_of_findings,
            "runtime": self.runtime,
        }
        run_info.update(self.__run_info)
        return run_info

    def ensure_executed(self, detector_args: Dict[str, str], timeout: Optional[int], force_detect: bool,
                        current_timestamp: int, compile_timestamp: int, logger: Logger) -> None:
        if self.is_outdated(compile_timestamp) or force_detect:
            pass
        elif self.is_failure():
            logger.info("Error in previous {}. Skipping.".format(str(self)))
            logger.debug("Full exception:", exc_info=True)
            return
        elif self.is_success():
            logger.info("Successful previous %s. Skipping.", self)
            logger.info("Detector reported %s findings.", len(self.findings))
            return

        self.reset()

        logger.info("Running '%s' on %s ... (%s)", self.detector, self.version, time.strftime("%H:%M"))

        detector_args.update({
            key_findings_file: self._findings_file_path,
            key_run_file: self._run_file_path
        })

        self._execute(detector_args, timeout, current_timestamp, logger)

        if not self.is_success():
            logger.info("Run {} failed.".format(str(self)))
            logger.debug("Full exception:", exc_info=True)
        else:
            logger.info("Detector reported %s findings.", len(self.findings))

    def _execute(self, detector_args: Dict[str, str], timeout: Optional[int], current_timestamp: int, logger: Logger):
        start = time.time()
        message = ""
        try:
            self.detector.execute(self.version, detector_args, timeout, logger)
            result = Result.success
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

        self.__save_run_info(result, runtime, message, self.detector.md5, current_timestamp)

    def __save_run_info(self, result, runtime, message, detector_md5, current_timestamp):
        # load and update, since an execution might have written additional fields to the file since initialization
        run_info = self.__load_run_info()
        run_info.update({
            "result": result.name,
            "runtime": runtime,
            "message": message,
            "timestamp": current_timestamp,
            "md5": detector_md5
        })
        write_yaml(run_info, file=self._run_file_path)
        self.__RUN_INFO = run_info

    @property
    def findings(self) -> List[Finding]:
        if not self.__FINDINGS:
            self.__FINDINGS = self._load_findings()
        return self.__FINDINGS

    @property
    def number_of_findings(self):
        return len(self.findings)

    def _load_findings(self):
        with open_yamls_if_exists(self._findings_file_path) as findings:
            return [self.__create_finding(rank, data) for rank, data in enumerate(findings) if data]

    @staticmethod
    def __create_finding(rank: int, finding_data: Dict):
        finding_data["rank"] = rank
        return Finding(finding_data)

    def reset(self):
        remove_tree(self.findings_path)
        makedirs(self.findings_path, exist_ok=True)
        DetectorRun.__init__(self, self.detector, self.version, self.findings_path)

    def is_success(self):
        return self.result == Result.success

    def is_error(self):
        return self.result == Result.error

    def is_timeout(self):
        return self.result == Result.timeout

    def is_failure(self):
        return self.is_error() or self.is_timeout()

    def is_outdated(self, compile_timestamp: int):
        return self._is_outdated_detector() or self._newer_compile(compile_timestamp)

    def _is_outdated_detector(self):
        return self.detector.md5 != self.__detector_md5

    def _newer_compile(self, compile_timestamp: int):
        return self.__timestamp < compile_timestamp

    def __str__(self):
        return "run on {}".format(self.version)
