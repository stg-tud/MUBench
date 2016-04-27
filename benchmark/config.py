import sys
from enum import Enum
from os.path import join
from tempfile import gettempdir

# These settings are shared between all modules
# IMPORTANT:    always import settings and use settings like settings.DATA_PATH!
#               (don't use from settings import <setting>)
#               Doing it this way allows tests to alter these values
#               See http://effbot.org/zone/import-confusion.htm for more detail
from typing import Any


class Config:
    DATA_PATH = "./data"
    MISUSE_DETECTOR_PATH = "./detectors"
    MISUSE_DETECTOR = "dummy-miner"
    FILE_DETECTOR_RESULT = "result.txt"
    RESULTS_PATH = "../MUBenchmark-results"
    CHECKOUT_DIR = "../MUBenchmark-checkouts"
    TIMEOUT = None
    BLACK_LIST = []
    WHITE_LIST = [""]
    LOG_DETECTOR_ERROR = "error.log"
    LOG_DETECTOR_OUT = "out.log"

    # derived values (must be updated in update!)
    BENCHMARK_RESULT_FILE = join(RESULTS_PATH, 'benchmark-result.txt')
    LOG_PATH = join(RESULTS_PATH, "_LOGS")
    LOG_FILE_ERROR = join(LOG_PATH, "error.log")
    LOG_FILE_CHECKOUT = join(LOG_PATH, "checkout.log")
    LOG_FILE_RESULTS_EVALUATION = join(LOG_PATH, "results-evaluation.log")

    @staticmethod
    def update_derived_values() -> None:
        Config.BENCHMARK_RESULT_FILE = join(Config.RESULTS_PATH, 'benchmark-result.txt')
        Config.LOG_PATH = join(Config.RESULTS_PATH, "_LOGS")
        Config.LOG_FILE_ERROR = join(Config.LOG_PATH, "error.log")
        Config.LOG_FILE_CHECKOUT = join(Config.LOG_PATH, "checkout.log")
        Config.LOG_FILE_RESULTS_EVALUATION = join(Config.LOG_PATH, "results-evaluation.log")
