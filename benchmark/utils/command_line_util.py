from argparse import ArgumentParser, HelpFormatter
from operator import attrgetter

from typing import List, Any


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


def get_command_line_parser(available_detectors: List[str]) -> ArgumentParser:
    parser = ArgumentParser(
        description="Run MUBench, the benchmark for API-misuse detectors.",
        epilog="For details, check out https://github.com/stg-tud/MUBench.",
        formatter_class=SortingHelpFormatter)

    subparsers = parser.add_subparsers(
        help="MUBench provides several subprocesses. Run `benchmark.py <subprocess> -h` for details.",
        dest='subprocess')

    __add_check_subprocess(subparsers)
    __add_checkout_subprocess(subparsers)
    __add_compile_subprocess(subparsers)
    __add_detect_subprocess(available_detectors, subparsers)
    __add_evaluate_subprocess(available_detectors, subparsers)
    __add_visualize_subprocess(subparsers)

    return parser


def parse_args(args: List[str], available_detectors) -> Any:
    parser = get_command_line_parser(available_detectors)

    # remove first arg which always contains the script name
    args = args[1:]

    # add an invalid mode if no mode was given
    if not args:
        args.append("")

    return parser.parse_args(args)


def __add_check_subprocess(subparsers) -> None:
    subparsers.add_parser('check', formatter_class=SortingHelpFormatter,
                          help="Validate whether the environment meets the prerequisites to run MUBench.")  # type: ArgumentParser


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


def __add_evaluate_subprocess(available_detectors: List[str], subparsers) -> None:
    eval_parser = subparsers.add_parser('eval', formatter_class=SortingHelpFormatter,
                                        description="Evaluate detection results. Run `detect` if necessary. Write results to `results/<detector>/result.csv`.",
                                        help="Evaluate detection results. Run `detect` if necessary. Write results to `results/<detector>/result.csv`." +
                                             "Run `eval -h` to see a list of available detectors.")  # type: ArgumentParser
    __setup_misuse_filter_arguments(eval_parser)
    __setup_checkout_arguments(eval_parser)
    __setup_compile_arguments(eval_parser)
    __setup_detector_arguments(eval_parser, available_detectors)


def __add_visualize_subprocess(subparsers) -> None:
    subparsers.add_parser('visualize', formatter_class=SortingHelpFormatter,
                          description="Collect all detect and manual review results and write them to `results/result.csv`",
                          help="Collect all detect and manual review results and write them to `results/result.csv`")  # type: ArgumentParser


def __setup_misuse_filter_arguments(parser: ArgumentParser):
    parser.add_argument('--only', metavar='X', nargs='+', dest='white_list', default=[],
                        help="process only misuses whose names contain any of the given strings")
    parser.add_argument('--skip', metavar='Y', nargs='+', dest='black_list', default=[],
                        help="skip all misuses whose names contain any of the given strings")


def __setup_checkout_arguments(parser: ArgumentParser):
    parser.add_argument('--force-checkout', dest='force_checkout', action='store_true', default=False,
                        help="force a clean checkout, deleting any existing files")


def __setup_compile_arguments(parser: ArgumentParser):
    parser.add_argument('--force-compile', dest='force_compile', action='store_true', default=False,
                        help="force a clean compilation")


def __setup_detector_arguments(parser: ArgumentParser, available_detectors: List[str]) -> None:
    parser.add_argument('detector', help="the detector whose findings to evaluate",
                        choices=available_detectors)
    parser.add_argument('--force-detect', dest='force_detect', action='store_true', default=False,
                        help="force a new `detect` run, deleting the previous result")
    parser.add_argument('--timeout', type=int, default=None, metavar='s',
                        help="abort detection of a misuse after the provided number of seconds (if it needs to be run) and skip the misuse")
    parser.add_argument('--java-options', metavar='option', nargs='+', dest='java_options', default=[],
                        help="will be passed to the java subprocess running the detector (example: `--java-options Xmx6144M` will run `java -Xmx6144M`)")
