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
                 src_normal_subdir: str,
                 classes_normal_subdir: str,
                 src_patterns_subdir: str,
                 classes_patterns_subdir: str,
                 results_path: str,
                 timeout: Optional[int],
                 java_options: List[str]):
        self.detector = detector
        self.detector_result_file = detector_result_file
        self.checkout_base_dir = checkout_base_dir
        self.src_normal_subdir = src_normal_subdir
        self.classes_normal_subdir = classes_normal_subdir
        self.src_patterns_subdir = src_patterns_subdir
        self.classes_patterns_subdir = classes_patterns_subdir
        self.results_path = results_path
        self.timeout = timeout
        self.java_options = ['-' + option for option in java_options]

    def run_detector(self, misuse: Misuse) -> None:
        result_dir = join(self.results_path, misuse.name)

        project_name = misuse.project_name
        project_dir = join(self.checkout_base_dir, project_name)

        with safe_open(join(result_dir, "out.log"), 'w+') as out_log:
            with safe_open(join(result_dir, "error.log"), 'w+') as error_log:
                try:
                    absolute_misuse_detector_path = Detect.__get_misuse_detector_path(self.detector)

                    src_normal = join(project_dir, self.src_normal_subdir)
                    src_patterns = join(project_dir, self.src_patterns_subdir)
                    detector_args = [src_normal, src_patterns, join(result_dir, self.detector_result_file)]
                    if misuse.build_config is not None:
                        classes_normal = join(project_dir, self.classes_normal_subdir)
                        classes_patterns = join(project_dir, self.classes_patterns_subdir)
                        detector_args += [classes_normal, classes_patterns]

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
