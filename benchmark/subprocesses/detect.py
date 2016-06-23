import subprocess
import time
from os.path import join, realpath, exists, dirname
from typing import Optional, List

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils import web_util
from benchmark.utils.io import safe_open, safe_write
from benchmark.utils.printing import subprocess_print


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
        result_path = join(self.results_base_path, misuse.name)
        project_compile = misuse.get_compile(self.compiles_base_path)

        with safe_open(join(result_path, "out.log"), 'w+') as out_log:
            with safe_open(join(result_path, "error.log"), 'w+') as error_log:
                try:
                    absolute_misuse_detector_path = Detect.__get_misuse_detector_path(self.detector)

                    findings_file = [self.key_findings_file, join(result_path, self.detector_findings_file)]
                    src_project = [self.key_src_project, project_compile.original_sources_path]
                    src_patterns = []
                    classes_project = []
                    classes_patterns = []

                    if misuse.patterns:
                        src_patterns = [self.key_src_patterns, project_compile.pattern_sources_path]

                    if misuse.build_config.commands:
                        classes_project = [self.key_classes_project, project_compile.original_classes_path]
                        if misuse.patterns:
                            classes_patterns = [self.key_classes_patterns, project_compile.pattern_classes_path]

                    detector_args = findings_file + src_project + src_patterns + classes_project + classes_patterns

                    subprocess_print("Detect : running... ", end='')
                    start = time.time()
                    returncode = self._invoke_detector(absolute_misuse_detector_path, detector_args, out_log, error_log)
                    end = time.time()
                    runtime = end - start

                    if returncode == 0:
                        print("ok. Took {0:.2f}s.".format(runtime))
                        return DataReaderSubprocess.Answer.ok
                    else:
                        print("error! Check logs in the results folder.")
                        return DataReaderSubprocess.Answer.skip

                except subprocess.TimeoutExpired:
                    print("timeout!", flush=True)
                    safe_write("Timeout: {}".format(misuse.name), error_log, append=True)
                    return DataReaderSubprocess.Answer.skip

    def _invoke_detector(self, absolute_misuse_detector_path: str, detector_args: List[str], out_log, error_log):
        return subprocess.call(["java"] + self.java_options + ["-jar", absolute_misuse_detector_path] + detector_args,
                               bufsize=1, stdout=out_log, stderr=error_log, timeout=self.timeout)

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
