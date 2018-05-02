from argparse import HelpFormatter, ArgumentParser
from operator import attrgetter

import sys


parser = ArgumentParser(
    prog="./mubench browse",
    description="Browse MUBench docker volumes.",
    epilog="For details, check out "
           "https://github.com/stg-tud/MUBench/tree/master/mubench.pipeline#experiment-data.")

parser.parse_args(sys.argv)
