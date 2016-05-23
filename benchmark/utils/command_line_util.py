from argparse import ArgumentParser

from typing import List, Any


def get_command_line_parser(available_detectors: List[str]) -> ArgumentParser:
    parser = ArgumentParser(
        description="Run MUBench, the benchmark for API-misuse detectors.",
        epilog="For details, check out https://github.com/stg-tud/MUBench.")

    subparsers = parser.add_subparsers(
        help="MUBench provides several subprocesses. Run `benchmark.py <subprocess> -h` for details.",
        dest='subprocess')

    __add_check_subprocess(subparsers)
    __add_checkout_subprocess(subparsers)
    __add_detect_subprocess(available_detectors, subparsers)
    __add_evaluate_subprocess(available_detectors, subparsers)

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
    subparsers.add_parser('check',
                          help="Validate whether the environment meets the prerequisites to run MUBench.")  # type: ArgumentParser


def __add_checkout_subprocess(subparsers) -> None:
    checkout_parser = subparsers.add_parser('checkout',
                                            description="Clone the repositories containing the misuses from the MUBench dataset. The clones will be created below the `checkouts` folder.",
                                            help="Clone the repositories containing the misuses from the MUBench dataset. The clones will be created below the `checkouts` folder.")  # type: ArgumentParser
    checkout_parser.add_argument('--only', metavar='X', nargs='+', dest='white_list', default=[""],
                                 help="clone only the repositories for the misuses whose names contain any of the given strings")

    checkout_parser.add_argument('--skip', metavar='Y', nargs='+', dest='black_list', default=[],
                                 help="skip the repositories for the misuses whose names contain any of the given strings")


def __add_detect_subprocess(available_detectors: List[str], subparsers) -> None:
    detect_parser = subparsers.add_parser('detect',
                                          description="Run a detector on the repositories containing the misuses from the MUBench dataset. Run `checkout` if necessary.",
                                          help="Run a detector on the repositories containing the misuses from the MUBench dataset. Run `checkout` if necessary. " +
                                               "Run `detect -h` to see a list of available detectors.",
                                          epilog="The results are written to `results/<detector>/<misuse>/`.")  # type: ArgumentParser
    __setup_detector_running_subprocess(available_detectors, detect_parser)


def __add_evaluate_subprocess(available_detectors: List[str], subparsers) -> None:
    eval_parser = subparsers.add_parser('eval',
                                        description="Evaluate detection results. Run `detect` if necessary. Write results to `results/<detector>/Results.txt`.",
                                        help="Evaluate detection results. Run `detect` if necessary. Write results to `results/<detector>/Results.txt`." +
                                             "Run `eval -h` to see a list of available detectors.")  # type: ArgumentParser
    __setup_detector_running_subprocess(available_detectors, eval_parser)


def __setup_detector_running_subprocess(available_detectors: List[str], subprocess_parser: ArgumentParser) -> None:
    subprocess_parser.add_argument('detector', help="the detector whose findings to evaluate",
                                   choices=available_detectors)

    subprocess_parser.add_argument('--only', metavar='X', nargs='+', dest='white_list', default=[""],
                                   help="consider only the misuses whose names contain any of the given strings")

    subprocess_parser.add_argument('--skip', metavar='Y', nargs='+', dest='black_list', default=[],
                                   help="ignore all misuses whose names contain any of the given strings")

    subprocess_parser.add_argument('--timeout', type=int, default=None, metavar='s',
                                   help="abort detection of a misuse after the provided number of seconds (if it needs to be run) and pretend the detector failed to find anything")

    subprocess_parser.add_argument('--java-options', metavar='option', nargs='+', dest='java_options', default=[],
                                   help="will be passed to the java subprocess running the detector (example: `--java-options Xmx6144M` will run `java -Xmx6144M`")
