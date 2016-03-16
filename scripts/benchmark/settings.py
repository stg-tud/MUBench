# These settings are shared between all benchmark modules

DATA_PATH = r"<...>\MUBench\data"  # path to the data folder
FILE_BENCHMARK_RESULT = r"<result>"  # where the final result will be written
RESULTS_PATH = r"<output_path>"  # used for saving intermediate results
TEMP_SUBFOLDER = "<subfolder>"  # used as subfolder in the temp path (will show up in misuse detection results)
MISUSE_DETECTOR = r"<path_to_jar>"  # path to the misuse detector to benchmark (must be an executable .jar)
FILE_DETECTOR_RESULT = "finalAnomalies.txt"  # result written by the misuse detector
VERBOSE = True  # prints more information to console if True
