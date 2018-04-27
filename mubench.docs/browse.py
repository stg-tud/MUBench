from argparse import HelpFormatter, ArgumentParser
from operator import attrgetter

import sys


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


parser = ArgumentParser(
    prog="./mubench browse",
    description="Browse MUBench docker volumes.",
    epilog="For details, check out "
           "https://github.com/stg-tud/MUBench/tree/master/mubench.pipeline#experiment-data.",
    formatter_class=SortingHelpFormatter)

parser.parse_args(sys.argv)
