import subprocess
import traceback
from genericpath import exists
from os import getcwd
from os.path import join, splitext, basename
from pprint import PrettyPrinter

from typing import List, Optional, Dict, Union

from benchmark.checkout import Checkout
from benchmark.datareader import on_all_data_do
from benchmark.utils.data_util import extract_project_name_from_file_path
from benchmark.utils.io import safe_open, safe_write
from benchmark.utils.printing import subprocess_print, print_ok

CATCH_ERRORS = True  # only used for testing


class DetectorRunner:
    def __init__(self,
                 data_path: str,
                 detector: str,
                 checkout_base_dir: str,
                 results_path: str,
                 timeout: Optional[int],
                 white_list: List[str],
                 black_list: List[str],
                 catch_errors: bool = True):
        self.data_path = data_path
        self.detector = detector
        self.checkout_base_dir = checkout_base_dir
        self.results_path = results_path
        self.timeout = timeout
        self.catch_errors = catch_errors
        self.white_list = white_list
        self.black_list = black_list

    def run_detector(self, file: str, misuse: Dict[str, Union[str, Dict]]) -> None:
        try:
            result_dir = join(self.results_path, splitext(basename(file))[0])

            project_name = extract_project_name_from_file_path(file)
            checkout_dir = join(self.checkout_base_dir, project_name)

            checkout_successful = Checkout(True, True).checkout(file, misuse)
            if not checkout_successful:
                return

            with safe_open(join(result_dir, "out.log"), 'w+') as out_log:
                with safe_open(join(result_dir, "error.log"), 'w+') as error_log:
                    try:
                        absolute_misuse_detector_path = DetectorRunner.__get_misuse_detector_path(self.detector)

                        subprocess_print("Detect - running detector... ", end='')

                        subprocess.call(["java", "-jar", absolute_misuse_detector_path, checkout_dir, result_dir],
                                        bufsize=1, stdout=out_log, stderr=error_log, timeout=self.timeout)

                        print_ok()

                    except subprocess.TimeoutExpired:
                        print("timeout!")
                        safe_write("Timeout: {}".format(file), error_log, append=True)
                        return

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            if not CATCH_ERRORS:
                raise

            exception_string = traceback.format_exc()
            safe_write("Error: {} in {}".format(exception_string, file), join(self.results_path, '_LOGS', 'error.log'),
                       append=True)

    def run_detector_on_all_data(self) -> List[None]:
        on_all_data_do(self.data_path, self.run_detector, self.white_list, self.black_list)

    @staticmethod
    def __get_misuse_detector_path(detector: str):
        return join(getcwd(), "detectors", detector, detector + '.jar')
