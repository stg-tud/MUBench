from argparse import HelpFormatter, ArgumentParser
from operator import attrgetter

import sys


__TASKS = ['pipeline', 'browse', 'reviewsite', 'update']


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


parser = ArgumentParser(
    prog="./mubench",
    description="Run MUBench, the benchmark for API-misuse detectors.",
    epilog="For details, check out https://github.com/stg-tud/MUBench.",
    formatter_class=SortingHelpFormatter)

parser.add_argument('task', nargs='?', choices=__TASKS, default='pipeline',
                    help="MUBench supports several tasks. "
                         "Run `mubench <task> -h` for details.")

parser.parse_args(sys.argv[1:])
