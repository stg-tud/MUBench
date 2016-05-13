import subprocess
from genericpath import exists
from os.path import join, splitext, basename, realpath
from typing import Optional, Dict, Union

from benchmark.utils.data_util import extract_project_name_from_file_path
from benchmark.utils.io import safe_open, safe_write
from benchmark.utils.printing import subprocess_print, print_ok


class Detect:
    def __init__(self,
                 detector: str,
                 detector_result_file: str,
                 checkout_base_dir: str,
                 results_path: str,
                 timeout: Optional[int]):
        self.detector = detector
        self.detector_result_file = detector_result_file
        self.checkout_base_dir = checkout_base_dir
        self.results_path = results_path
        self.timeout = timeout

    def run_detector(self, file: str, misuse: Dict[str, Union[str, Dict]]) -> None:
        result_dir = join(self.results_path, splitext(basename(file))[0])

        project_name = extract_project_name_from_file_path(file)
        checkout_dir = join(self.checkout_base_dir, project_name)

        with safe_open(join(result_dir, "out.log"), 'w+') as out_log:
            with safe_open(join(result_dir, "error.log"), 'w+') as error_log:
                try:
                    absolute_misuse_detector_path = Detect.__get_misuse_detector_path(self.detector)

                    detector_args = [checkout_dir, join(result_dir, self.detector_result_file)]

                    pattern_file = join(splitext(file)[0], '.pattern')
                    if exists(pattern_file):
                        detector_args.append(pattern_file)

                    subprocess_print("Detect : running... ", end='')
                    subprocess.call(["java", "-jar", absolute_misuse_detector_path] + detector_args,
                                    bufsize=1, stdout=out_log, stderr=error_log, timeout=self.timeout)

                    print_ok()

                except subprocess.TimeoutExpired:
                    print("timeout!", flush=True)
                    safe_write("Timeout: {}".format(file), error_log, append=True)
                    return

    @staticmethod
    def __get_misuse_detector_path(detector: str):
        return realpath(join("detectors", detector, detector + '.jar'))
