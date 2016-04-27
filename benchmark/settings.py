import sys
from os.path import join
from tempfile import gettempdir

# These settings are shared between all modules
# IMPORTANT:    always import settings and use settings like settings.DATA_PATH!
#               (don't use from settings import <setting>)
#               Doing it this way allows tests to alter these values
#               See http://effbot.org/zone/import-confusion.htm for more detail

# --- set these values ---
# path to the MUBench data folder
DATA_PATH = r"./data"
# path to the misuse detector to benchmark (must be an executable .jar)
MISUSE_DETECTOR = r"./detectors"
# name of the result files written by the given misuse detector
FILE_DETECTOR_RESULT = "result.txt"
# the path given to the misuse detector as its result output folder
RESULTS_PATH = "../MUBenchmark-results"
# ------------------------


# --- you might want to set these values ---
# where the final result will be written
BENCHMARK_RESULT_FILE = join(RESULTS_PATH, 'benchmark-result.txt')
# where the log files will be written
LOG_PATH = join(RESULTS_PATH, "_LOGS")
# where the projects will be checked out
CHECKOUT_DIR = "../MUBenchmark-checkouts"
# sets a timeout for the misuse detector (in seconds); will ignore timed out cases in the results
# None disables the timeout
TIMEOUT = None
# all data files which contain this substring will be ignored by the benchmark
BLACK_LIST = []
# only datafiles which contain one of these strings will be use by the benchmark
WHITE_LIST = [""]  # default [""] enables all data (since "" is a substring of every string)
# ------------------------------------------


# --- you probably don't need to change these values ---
# errors are logged in this file
LOG_FILE_ERROR = join(LOG_PATH, "error.log")
# checkout output is logged in this file
LOG_FILE_CHECKOUT = join(LOG_PATH, "checkout.log")
# result evaluation output is logged in this file
LOG_FILE_RESULTS_EVALUATION = join(LOG_PATH, "results-evaluation.log")
# contains errors thrown by the detector (will be in the result folder for the given case)
LOG_DETECTOR_ERROR = "error.log"
# contains console output of the detector (will be in the result folder for the given case)
LOG_DETECTOR_OUT = "out.log"
# ------------------------------------------------------
