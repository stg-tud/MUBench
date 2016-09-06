from argparse import ArgumentParser, HelpFormatter
from operator import attrgetter

from typing import List, Any


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


class CaseInsensitiveChoices(list):
    def __init__(self, iterable):
        super().__init__(iterable)

    def __contains__(self, other):
        return any([element for element in self if element.lower() == other.lower()])


def get_command_line_parser(available_detectors: List[str], available_scripts: List[str]) -> ArgumentParser:
    available_detectors = CaseInsensitiveChoices(available_detectors)
    available_scripts = CaseInsensitiveChoices(available_scripts)

    parser = ArgumentParser(
        description="Run MUBench, the benchmark for API-misuse detectors.",
        epilog="For details, check out https://github.com/stg-tud/MUBench.",
        formatter_class=SortingHelpFormatter)

    subparsers = parser.add_subparsers(
        help="MUBench provides several tasks. Run `mubench <task> -h` for details.",
        dest='subprocess')

    __add_check_subprocess(subparsers)
    __add_info_subprocess(subparsers)
    __add_checkout_subprocess(subparsers)
    __add_compile_subprocess(subparsers)
    __add_detect_subprocess(available_detectors, subparsers)
    __add_review_prepare_subprocess(subparsers)
    __add_review_check_subprocess(subparsers)
    __add_visualize_subprocess(subparsers)
    __add_stats_subprocess(available_scripts, subparsers)

    return parser


def parse_args(args: List[str], available_detectors: List[str], available_scripts: List[str]) -> Any:
    parser = get_command_line_parser(available_detectors, available_scripts)

    # remove first arg which always contains the script name
    args = args[1:]

    # add an invalid mode if no mode was given
    if not args:
        args.append("")

    return parser.parse_args(args)


def __add_check_subprocess(subparsers) -> None:
    subparsers.add_parser('check', formatter_class=SortingHelpFormatter,
                          help="Validate whether the environment meets the prerequisites to run MUBench.")  # type: ArgumentParser


def __add_info_subprocess(subparsers) -> None:
    parser = subparsers.add_parser('info', formatter_class=SortingHelpFormatter,
                          help="Show info about projects, project versions, and misuses in MUBench.")
    __setup_misuse_filter_arguments(parser)


def __add_checkout_subprocess(subparsers) -> None:
    checkout_parser = subparsers.add_parser('checkout', formatter_class=SortingHelpFormatter,
                                            description="Clone the repositories containing the misuses from the MUBench dataset. The clones will be created below the `checkouts` folder.",
                                            help="Clone the repositories containing the misuses from the MUBench dataset. The clones will be created below the `checkouts` folder.")  # type: ArgumentParser
    __setup_misuse_filter_arguments(checkout_parser)
    __setup_checkout_arguments(checkout_parser)


def __add_compile_subprocess(subparsers) -> None:
    compile_parser = subparsers.add_parser('compile', formatter_class=SortingHelpFormatter,
                                           description="Compile the checkouts and the the patterns. Run `checkout`, if necessary.",
                                           help="Compile the checkouts and the patterns. Run `checkout`, if necessary.")
    __setup_misuse_filter_arguments(compile_parser)
    __setup_compile_arguments(compile_parser)
    __setup_checkout_arguments(compile_parser)


def __add_detect_subprocess(available_detectors: List[str], subparsers) -> None:
    detect_parser = subparsers.add_parser('detect', formatter_class=SortingHelpFormatter,
                                          description="Run a detector on the checkouts. Run `compile` before.",
                                          help="Run a detector on the checkouts. Run `compile` before. " +
                                               "Run `detect -h` to see a list of available detectors.",
                                          epilog="The results are written to `results/<detector>/<misuse>/`.")  # type: ArgumentParser
    __setup_misuse_filter_arguments(detect_parser)
    __setup_detector_arguments(detect_parser, available_detectors)
    __setup_checkout_arguments(detect_parser)
    __setup_compile_arguments(detect_parser)


def __add_review_prepare_subprocess(subparsers) -> None:
    review_prepare_parser = subparsers.add_parser('review:prepare', formatter_class=SortingHelpFormatter,
                                                  description="Prepare findings for reviewing.",  # TODO: more detail?
                                                  help="Prepare findings for reviewing.")  # type: ArgumentParser
    review_prepare_parser.add_argument('experiment', help="the experiment to prepare reviews for",
                                       choices=["1", "2", "3"])
    __setup_misuse_filter_arguments(review_prepare_parser)
    review_prepare_parser.add_argument('--only-detectors', metavar='D', nargs='+', dest="detector_white_list",
                                       default=[], help="prepare only for the detectors whose names are given")
    review_prepare_parser.add_argument('--force-prepare', dest='force_prepare', action='store_true', default=False,
                                       help="force generating new review files")
    review_prepare_parser.add_argument('--top-n', metavar='N', dest="top_n_findings", type=int, default=10,
                                       help="include the top-n findings in experiment 3 review pages")


def __add_review_check_subprocess(subparsers) -> None:
    review_check_parser = subparsers.add_parser('review:check',
                                                formatter_class=SortingHelpFormatter)  # TODO: add description and help texts
    review_check_parser.add_argument('experiment', help="the experiment to check reviews for",
                                     choices=["1", "2", "3"])

def __add_visualize_subprocess(subparsers) -> None:
    subparsers.add_parser('visualize', formatter_class=SortingHelpFormatter,
                          description="Collect all detect and manual review results and write them to `results/result.csv`",
                          help="Collect all detect and manual review results and write them to `results/result.csv`")  # type: ArgumentParser


def __add_stats_subprocess(available_scripts: List[str], subparsers) -> None:
    stats_parser = subparsers.add_parser('stats', formatter_class=SortingHelpFormatter,
                                         description="Calculate statistics using the given script",
                                         help="Calculate statistics using the given script")  # type: ArgumentParser
    stats_parser.add_argument('script', help="the calculation strategy to use (case insensitive)",
                              choices=available_scripts)
    __setup_misuse_filter_arguments(stats_parser)


def __setup_misuse_filter_arguments(parser: ArgumentParser):
    parser.add_argument('--only', metavar='X', nargs='+', dest='white_list', default=[],
                        help="process only projects or project versions whose names are given")
    parser.add_argument('--skip', metavar='Y', nargs='+', dest='black_list', default=[],
                        help="skip all projects or project versions whose names are given")


def __setup_checkout_arguments(parser: ArgumentParser):
    parser.add_argument('--force-checkout', dest='force_checkout', action='store_true', default=False,
                        help="force a clean checkout, deleting any existing files")


def __setup_compile_arguments(parser: ArgumentParser):
    parser.add_argument('--force-compile', dest='force_compile', action='store_true', default=False,
                        help="force a clean compilation")
    parser.add_argument('--pattern-frequency', dest='pattern_frequency', default=1,
                        help='the frequency of generated fix patterns', type=int)


def __setup_detector_arguments(parser: ArgumentParser, available_detectors: List[str]) -> None:
    parser.add_argument('detector', help="the detector whose findings to evaluate",
                        choices=available_detectors)
    parser.add_argument('experiment', help="configures the detector for the experiment", type=int,
                        choices=[1, 2, 3])
    parser.add_argument('--force-detect', dest='force_detect', action='store_true', default=False,
                        help="force a new `detect` run, deleting the previous result")
    parser.add_argument('--timeout', type=int, default=None, metavar='s',
                        help="abort detection of a misuse after the provided number of seconds (if it needs to be run) and skip the misuse")
    parser.add_argument('--java-options', metavar='option', nargs='+', dest='java_options', default=[],
                        help="will be passed to the java subprocess running the detector (example: `--java-options Xmx6144M` will run `java -Xmx6144M`)")

