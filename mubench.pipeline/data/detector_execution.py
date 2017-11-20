import time
from enum import Enum
from logging import Logger
from os import makedirs
from typing import Optional, List, Dict

from data.detector import Detector
from data.finding import Finding, SpecializedFinding
from data.findings_filters import FindingsFilter
from data.project_version import ProjectVersion
from utils.io import write_yaml, remove_tree, read_yaml_if_exists, open_yamls_if_exists
from utils.shell import CommandFailedError


class Result(Enum):
    error = 0
    success = 1
    timeout = 2


class DetectorExecution:
    def __init__(self, detector: Detector, version: ProjectVersion, findings_path: str,
                 findings_filter: FindingsFilter, findings_file_path: str, run_file_path: str):
        self.detector = detector
        self.version = version
        self._findings_filter = findings_filter
        self._findings_path = findings_path
        self.__FINDINGS = None
        self.__POTENTIAL_HITS = None
        self.__run_info = None
        self._findings_file_path = findings_file_path
        self._run_file_path = run_file_path

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
        return self.__get_run_info("runtime", 0)

    @property
    def message(self):
        return self.__get_run_info("message", "")

    @property
    def __detector_md5(self):
        return self.__get_run_info("md5", None)

    def get_run_info(self):
        run_info = {
            "number_of_findings": self.number_of_findings,
            "runtime": self.runtime
        }
        return run_info.update(self.__run_info)

    def execute(self, detector_args: Dict[str, str], timeout: Optional[int], logger: Logger):
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
            self.__POTENTIAL_HITS = self.detector.specialize_findings(self._findings_path, potential_hits)
        return self.__POTENTIAL_HITS

    @property
    def __findings(self) -> List[Finding]:
        if not self.__FINDINGS:
            self.__FINDINGS = self._load_findings()
        return self.__FINDINGS

    @property
    def number_of_findings(self):
        return len(self.__findings)

    def _load_findings(self):
        with open_yamls_if_exists(self._findings_file_path) as findings:
            return [self.__create_finding(rank, data) for rank, data in enumerate(findings) if data]

    @staticmethod
    def __create_finding(rank: int, finding_data: Dict):
        finding_data["rank"] = rank
        return Finding(finding_data)

    def reset(self):
        remove_tree(self._findings_path)
        makedirs(self._findings_path, exist_ok=True)
        DetectorExecution.__init__(self, self.detector, self.version, self._findings_path,
                                   self._findings_filter, self._findings_file_path, self._run_file_path)

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
        return "run on {}".format(self.version)
