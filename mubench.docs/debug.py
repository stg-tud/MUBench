from argparse import HelpFormatter, ArgumentParser
from operator import attrgetter
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../mubench.pipeline")
from utils.config_util import SortingHelpFormatter, __sort_subactions_by_name,\
 __DATASETS_FILE_PATH, \
 __add_run_ex1_subprocess, __add_run_ex2_subprocess, __add_run_ex3_subprocess

from data.detector import get_available_detector_ids, Detector
from utils.dataset_util import get_available_dataset_ids


available_datasets = get_available_dataset_ids(__DATASETS_FILE_PATH)

parser = ArgumentParser(
    prog="debug",
    description="Debug a detector on MUBench. "
                "Works similar to `pipeline run`, only that it halts the detector for attaching a remote debugger.",
    formatter_class=SortingHelpFormatter)

parser.add_argument('cli_version', help="The MUBench CLI version that the detector is using, e.g., '0.0.13'.")

debug_subparsers = parser.add_subparsers(dest='experiment',
                                         help="MUBench supports several experiments. "
                                              "Run `debug <experiment> -h` for details.")
__sort_subactions_by_name(debug_subparsers)
debug_subparsers.required = True

__add_run_ex1_subprocess(None, available_datasets, debug_subparsers)
__add_run_ex2_subprocess(None, available_datasets, debug_subparsers)
__add_run_ex3_subprocess(None, available_datasets, debug_subparsers)

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(2)

parser.parse_args(sys.argv[1:])
