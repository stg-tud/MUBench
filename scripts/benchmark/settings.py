from os import makedirs
from os.path import join

# These settings are shared between all modules
# IMPORTANT:    always import settings and use settings like settings.DATA_PATH!
#               (don't use from settings import <setting>)
#               Doing it this way allows tests to alter these values
#               See http://effbot.org/zone/import-confusion.htm for more detail

# INPUTS
DATA_PATH = r"...\MUBench\data"  # path to the data folder
MISUSE_DETECTOR = r"...\GROUMiner.jar"  # path to the misuse detector to benchmark (must be an executable .jar)
FILE_DETECTOR_RESULT = "finalAnomalies.txt"  # result written by the misuse detector

# OUTPUTS
RESULTS_PATH = r"...\result"  # used for saving intermediate results
BENCHMARK_RESULT_FILE = join(RESULTS_PATH, 'benchmark-result.txt')  # where the final result will be written

# LOGS
LOG_PATH = join(RESULTS_PATH, "_LOGS")
LOG_FILE_ERROR = join(LOG_PATH, "error.log")  # errors will be logged into this file
LOG_FILE_CHECKOUT = join(LOG_PATH, "checkout.log")
LOG_FILE_RESULTS_EVALUATION = join(LOG_PATH, "results-evaluation.log")

# BENCHMARK SETTINGS
TEMP_SUBFOLDER = "misuse-checkout"  # used as subfolder in the temp path (will show up in misuse detection results)
VERBOSE = True  # prints more information to console if True
IGNORES = []  # all data files which contain this substring will be ignored by the benchmark
