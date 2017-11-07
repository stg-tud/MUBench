import os
from os.path import join, dirname, abspath


class MubenchPaths:
    MUBENCH_ROOT_PATH = abspath(join(dirname(abspath(__file__)), os.pardir, os.pardir, os.pardir))
    DATA_PATH = join(MUBENCH_ROOT_PATH, "data")
    CHECKOUTS_PATH = join(MUBENCH_ROOT_PATH, "checkouts")
    COMPILES_PATH = CHECKOUTS_PATH
    DETECTORS_PATH = join(MUBENCH_ROOT_PATH, "detectors")
    FINDINGS_PATH = join(MUBENCH_ROOT_PATH, "findings")
    DATASETS_FILE_PATH = join(DATA_PATH, 'datasets.yml')
