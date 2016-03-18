from os.path import join

# These settings are shared between all modules
# IMPORTANT: always import settings and use settings like settings.DATA_PATH!
# Doing it this way allows tests to alter these values

DATA_PATH = r"E:\Eko\MUBench\data"  # path to the data folder
FILE_BENCHMARK_RESULT = r"<result>"  # where the final result will be written
RESULTS_PATH = r"<output_path>"  # used for saving intermediate results
TEMP_SUBFOLDER = "<subfolder>"  # used as subfolder in the temp path (will show up in misuse detection results)
MISUSE_DETECTOR = r"<path_to_jar>"  # path to the misuse detector to benchmark (must be an executable .jar)
FILE_DETECTOR_RESULT = "finalAnomalies.txt"  # result written by the misuse detector
LOG_FILE = join(RESULTS_PATH, "log.txt")  # errors will be logged into this file
VERBOSE = True  # prints more information to console if True
