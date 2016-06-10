from benchmark.data.misuse import Misuse
from benchmark.subprocesses.datareader import DataReaderSubprocess


def run_on_misuse(subprocess: DataReaderSubprocess, misuse: Misuse) -> DataReaderSubprocess.Answer:
    return subprocess.run(misuse)


def run_setup(subprocess: DataReaderSubprocess):
    subprocess.setup()


def run_teardown(subprocess: DataReaderSubprocess):
    subprocess.teardown()
