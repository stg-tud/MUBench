from argparse import HelpFormatter, ArgumentParser, _SubParsersAction, SUPPRESS
from operator import attrgetter

import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../mubench.pipeline")
from utils.shell import Shell, CommandFailedError


class CustomHelpFormatter(HelpFormatter):
    def _format_action(self, action):
        if type(action) == _SubParsersAction:
            msg = ''
            for subaction in action._get_subactions():
                msg += self._format_action(subaction)
            return msg
        else:
            return super(CustomHelpFormatter, self)._format_action(action)

try:
    __version__ = Shell.exec('version').strip()
except CommandFailedError as e:
    __version__ = "v???"

parser = ArgumentParser(
    usage=SUPPRESS,
    description="This is the MUBench Interactive Shell " + __version__ + ".",
    epilog="For details, check out `<command> -h` or https://github.com/stg-tud/MUBench.",
    add_help=False,
    formatter_class=CustomHelpFormatter)
    
parser.add_argument('-v', '--version', action='version', version=__version__, help=SUPPRESS)

parser._positionals.title = "Control MUBench via the following commands"
subparsers = parser.add_subparsers(dest='command')

subparsers.add_parser("pipeline",
                      help="Run benchmarking experiments, including checkout "
                           "and compilation of target projects, execution of "
                           "detectors, and publishing data to a review site.")
subparsers.add_parser("reviewsite",
                      help="Fire up a review site inside this container. The "
                           "site is available from the host system via "
                           "`http://localhost:8080/`.")
subparsers.add_parser("debug",
                      help="Run benchmark experiments for remote debugger of "
                           "of a detector from the host system.")
subparsers.add_parser("help",
                      help="Print this help message.")
subparsers.add_parser("update",
                      help="Update MUBench.")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)

parser.parse_args(sys.argv[1:])
