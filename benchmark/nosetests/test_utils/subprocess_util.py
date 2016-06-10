from benchmark.datareader import DataReaderSubprocess
from benchmark.misuse import Misuse


def run_on_misuse(subprocess: DataReaderSubprocess, misuse: Misuse) -> DataReaderSubprocess.Answer:
    return subprocess.run(misuse)


def run_setup(subprocess: DataReaderSubprocess):
    subprocess.setup()


def run_teardown(subprocess: DataReaderSubprocess):
    subprocess.teardown()
