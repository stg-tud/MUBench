from os import getcwd, chdir
from os.path import join, pardir, dirname, realpath


# These settings are shared between all modules
# IMPORTANT:    always import settings and use settings like settings.DATA_PATH!
#               (don't use from settings import <setting>)
#               Doing it this way allows tests to alter these values
#               See http://effbot.org/zone/import-confusion.htm for more detail


class Config:
    def __init__(self):
        mubench = join(dirname(__file__), pardir)
        chdir(mubench)  # set the cwd to the MUBench folder
        self.DATA_PATH = join(getcwd(), "data")
        self.DETECTOR = "dummy-miner"
        self.FILE_DETECTOR_RESULT = "result.txt"
        self.RESULTS_PATH = realpath(join("..", "MUBenchmark-results", self.DETECTOR))
        self.CHECKOUT_DIR = realpath(join("..", "MUBenchmark-checkouts"))
        self.TIMEOUT = None
        self.BLACK_LIST = []
        self.WHITE_LIST = [""]
