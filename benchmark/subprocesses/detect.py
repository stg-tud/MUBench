import logging
import subprocess
import time
from os.path import join, realpath, exists, dirname
from typing import Optional, List

from os import makedirs

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils import web_util
from benchmark.utils.io import safe_open, safe_write
from benchmark.utils.printing import subprocess_print
from benchmark.utils.shell import Shell, CommandFailedError


class Detect(DataReaderSubprocess):
    def __init__(self,
                 detector: str,
                 detector_result_file: str,
                 compiles_base_path: str,
                 results_base_path: str,
                 timeout: Optional[int],
                 java_options: List[str]):
        self.detector = detector
        self.detector_findings_file = detector_result_file
        self.compiles_base_path = compiles_base_path
        self.results_base_path = results_base_path
        self.timeout = timeout
        self.java_options = ['-' + option for option in java_options]

        self.key_findings_file = "target"
        self.key_src_project = "src"
        self.key_src_patterns = "src_patterns"
        self.key_classes_project = "classpath"
        self.key_classes_patterns = "classpath_patterns"

    def setup(self):
        if not self._detector_available():
            self._download()

    def run(self, misuse: Misuse) -> None:
        logger = logging.getLogger("detect")

        result_path = join(self.results_base_path, misuse.name)
        makedirs(result_path, exist_ok=True)
        project_compile = misuse.get_compile(self.compiles_base_path)

        try:
            absolute_misuse_detector_path = Detect.__get_misuse_detector_path(self.detector)

            findings_file = [self.key_findings_file, self.to_arg_path(join(result_path, self.detector_findings_file))]
            src_project = [self.key_src_project, self.to_arg_path(project_compile.original_sources_path)]
            src_patterns = []
            classes_project = []
            classes_patterns = []

            if misuse.patterns:
                src_patterns = [self.key_src_patterns, self.to_arg_path(project_compile.pattern_sources_path)]

            if misuse.build_config.commands:
                classes_project = [self.key_classes_project, self.to_arg_path(project_compile.original_classes_path)]
                if misuse.patterns:
                    classes_patterns = [self.key_classes_patterns, self.to_arg_path(project_compile.pattern_classes_path)]

            detector_args = findings_file + src_project + src_patterns + classes_project + classes_patterns

            logger.info("Detecting misuses...")
            logger.debug("- Detector args = %s", detector_args)
            logger = logging.getLogger("detect.run")
            start = time.time()
            self._invoke_detector(absolute_misuse_detector_path, detector_args)
            end = time.time()
            runtime = end - start
            logger.info("Detection took {0:.2f} seconds.".format(runtime))
            return DataReaderSubprocess.Answer.ok
        except CommandFailedError as e:
            logger.error("Detector failed: %s", e)
            return DataReaderSubprocess.Answer.skip
        except subprocess.TimeoutExpired:
            logger.error("Detector took longer than the maximum of %s seconds", self.timeout)
            return DataReaderSubprocess.Answer.skip

    def _invoke_detector(self, absolute_misuse_detector_path: str, detector_args: List[str]):
        command = ["java"] + self.java_options + ["-jar",
                                                  self.to_arg_path(absolute_misuse_detector_path)] + detector_args
        command = " ".join(command)
        return Shell.exec(command, logger=logging.getLogger("detect.run"), timeout=self.timeout)

    @staticmethod
    def to_arg_path(absolute_misuse_detector_path):
        return "\"{}\"".format(absolute_misuse_detector_path)

    def _detector_available(self) -> bool:
        return exists(Detect.__get_misuse_detector_path(self.detector))

    def _download(self) -> bool:
        return web_util.load_detector(Detect.__get_misuse_detector_url(self.detector),
                                      Detect.__get_misuse_detector_path(self.detector),
                                      Detect.__get_misuse_detector_md5(self.detector))

    @staticmethod
    def __get_misuse_detector_dir(detector: str):
        return realpath(join("detectors", detector))

    @staticmethod
    def __get_misuse_detector_path(detector: str):
        return join(Detect.__get_misuse_detector_dir(detector), detector + ".jar")

    @staticmethod
    def __get_misuse_detector_url(detector: str):
        return "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/{}.jar".format(detector)

    @staticmethod
    def __get_misuse_detector_md5(detector: str):
        return join(Detect.__get_misuse_detector_dir(detector), detector + ".md5")
