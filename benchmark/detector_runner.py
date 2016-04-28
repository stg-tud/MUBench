import subprocess
import traceback
from genericpath import exists
from os import getcwd
from os.path import join, splitext, basename
from typing import List, Optional, Dict, Union

from checkout import Checkout
from datareader import on_all_data_do
from utils.data_util import extract_project_name_from_file_path
from utils.io import safe_open, safe_write

CATCH_ERRORS = True  # only used for testing


class DetectorRunner:
    def __init__(self,
                 data_path: str,
                 detector: str,
                 checkout_base_dir: str,
                 results_path: str,
                 timeout: Optional[int] = None,
                 catch_errors: bool = True):
        self.data_path = data_path
        self.detector = detector
        self.checkout_base_dir = checkout_base_dir
        self.results_path = results_path
        self.timeout = timeout
        self.catch_errors = catch_errors

    def run_detector(self, file: str, misuse: Dict[str, Union[str, Dict]]) -> None:
        try:
            result_dir = join(self.results_path, splitext(basename(file))[0])

            fix = misuse["fix"]
            repository = fix["repository"]

            project_name = extract_project_name_from_file_path(file)
            checkout_dir = join(self.checkout_base_dir, project_name)

            if not exists(checkout_dir):
                Checkout.checkout_parent(repository["type"], repository["url"], fix.get('revision', ""), checkout_dir)
            else:
                Checkout.reset_to_revision(repository["type"], checkout_dir, fix.get('revision', ""))

            print("Running \'{}\'; Results in \'{}\'...".format(self.detector, result_dir))

            with safe_open(join(result_dir, "out.log"), 'w+') as out_log:
                with safe_open(join(result_dir, "error.log"), 'w+') as error_log:
                    try:
                        absolute_misuse_detector_path = DetectorRunner.__get_misuse_detector_path(self.detector)

                        subprocess.call(["java", "-jar", absolute_misuse_detector_path, checkout_dir, result_dir],
                                        bufsize=1, stdout=out_log, stderr=error_log, timeout=self.timeout)
                    except subprocess.TimeoutExpired:
                        timeout_message = "Timeout: {}".format(file)
                        print(timeout_message)
                        safe_write(timeout_message, error_log)
                        return

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            if not CATCH_ERRORS:
                raise

            exception_string = traceback.format_exc()
            print(exception_string)
            safe_write("Error: {} in {}".format(exception_string, file), join(self.results_path, '_LOGS', 'error.log'),
                       append=True)

    def run_detector_on_all_data(self) -> List[None]:
        on_all_data_do(self.data_path, self.run_detector)

    @staticmethod
    def __get_misuse_detector_path(detector: str):
        return join(getcwd(), "detectors", detector, detector + '.jar')
