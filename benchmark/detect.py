import subprocess
from os.path import join, realpath

from typing import Optional, List

from benchmark.misuse import Misuse
from benchmark.utils.io import safe_open, safe_write
from benchmark.utils.printing import subprocess_print, print_ok


class Detect:
    def __init__(self,
                 detector: str,
                 detector_result_file: str,
                 checkout_base_dir: str,
                 original_src_subdir: str,
                 original_classes_subdir: str,
                 patterns_src_subdir: str,
                 patterns_classes_subdir: str,
                 results_path: str,
                 timeout: Optional[int],
                 java_options: List[str]):
        self.detector = detector
        self.detector_findings_file = detector_result_file
        self.checkout_base_dir = checkout_base_dir
        self.project_src_subdir = original_src_subdir
        self.project_classes_subdir = original_classes_subdir
        self.patterns_src_subdir = patterns_src_subdir
        self.patterns_classes_subdir = patterns_classes_subdir
        self.results_path = results_path
        self.timeout = timeout
        self.java_options = ['-' + option for option in java_options]

        self.key_findings_file = "target"
        self.key_src_project = "src"
        self.key_src_patterns = "src_patterns"
        self.key_classes_project = "classpath"
        self.key_classes_patterns = "classpath_patterns"

    def run_detector(self, misuse: Misuse) -> None:
        result_dir = join(self.results_path, misuse.name)

        project_name = misuse.project_name
        project_dir = join(self.checkout_base_dir, project_name)

        with safe_open(join(result_dir, "out.log"), 'w+') as out_log:
            with safe_open(join(result_dir, "error.log"), 'w+') as error_log:
                try:
                    absolute_misuse_detector_path = Detect.__get_misuse_detector_path(self.detector)

                    findings_file = [self.key_findings_file, join(result_dir, self.detector_findings_file)]
                    src_project = [self.key_src_project, join(project_dir, self.project_src_subdir)]
                    src_patterns = []
                    classes_project = []
                    classes_patterns = []

                    if misuse.patterns:
                        src_patterns = [self.key_src_patterns, join(project_dir, self.patterns_src_subdir)]

                    if misuse.build_config is not None:
                        classes_project = [self.key_classes_project, join(project_dir, self.project_classes_subdir)]
                        if misuse.patterns:
                            classes_patterns = [self.key_classes_patterns,
                                                join(project_dir, self.patterns_classes_subdir)]

                    detector_args = findings_file + src_project + src_patterns + classes_project + classes_patterns

                    subprocess_print("Detect : running... ", end='')
                    returncode = self._invoke_detector(absolute_misuse_detector_path, detector_args, out_log, error_log)

                    if returncode == 0:
                        print_ok()
                    else:
                        print("Detector encountered an error! Logs can be found in the results folder.")

                except subprocess.TimeoutExpired:
                    print("timeout!", flush=True)
                    safe_write("Timeout: {}".format(misuse.name), error_log, append=True)
                    return

    def _invoke_detector(self, absolute_misuse_detector_path: str, detector_args: List[str], out_log, error_log):
        return subprocess.call(["java"] + self.java_options + ["-jar", absolute_misuse_detector_path] + detector_args,
                               bufsize=1, stdout=out_log, stderr=error_log, timeout=self.timeout)

    @staticmethod
    def __get_misuse_detector_path(detector: str):
        return realpath(join("detectors", detector, detector + '.jar'))
