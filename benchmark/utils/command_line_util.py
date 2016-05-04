from argparse import ArgumentParser

from typing import List, Any


def get_command_line_parser(available_detectors: List[str]) -> ArgumentParser:
    parser = ArgumentParser(prog="MUBench benchmark",
                            description="A benchmark for usage model miners and misuse detectors. The benchmark consists of several subprocesses.")

    subparsers = parser.add_subparsers(help="MUBench Subprocesses", dest='subprocess')

    __add_check_subprocess(subparsers)
    __add_checkout_subprocess(subparsers)
    __add_mine_subprocess(available_detectors, subparsers)
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


def __add_check_subprocess(subparsers):
    subparsers.add_parser('check', prog="MUBench benchmark prerequisites check",
                          help="This subprocess can be used to validate if all prerequisites to run the benchmark are met.")  # type: ArgumentParser


def __add_checkout_subprocess(subparsers):
    subparsers.add_parser('checkout',
                          help="This subprocess can be used to pre-load all projects used by the benchmark.\n" +
                               "The projects will be loaded into the `checkouts` folder. This is not configurable to keep MUBench self-contained.")  # type: ArgumentParser


def __add_mine_subprocess(available_detectors, subparsers):
    mine_parser = subparsers.add_parser(
        'detect',
        help="This subprocess expects an identifier for the detector to run. Use `py benchmark/benchmark.py eval -h` to see all runnable detectors.\n" +
             "Note that this also expects the detector to run on complete projects, hence it needs to generate its own usage models. This will probably be changed in the future to have a clean split between mine and eval.\n" +
             "This subprocess will implicitly load all projects into the `checkouts` folder.",
        epilog="You can find all MUBench data files in the `data` subfolder")  # type: ArgumentParser
    mine_parser.add_argument('detector', help="the detector to evaluate", choices=available_detectors)
    mine_parser.add_argument('--only', metavar='X', nargs='+', dest='white_list', default=[""],
                             help="runs the detector only on MUBench data files which contain any one of the given strings")
    mine_parser.add_argument('--ignore', metavar='Y', nargs='+', dest='black_list', default=[],
                             help="ignores MUBench data files which contain any one of the given strings")
    mine_parser.add_argument('--timeout', type=int, default=None, metavar='s',
                             help="will set a timeout (in seconds) for the misuse detector; cases where a timeout occurred will be ignored in the evaluation  ")


def __add_evaluate_subprocess(available_detectors, subparsers):
    mine_parser = subparsers.add_parser(
        'eval',
        help="This subprocess evaluates the results of a mining run. Hence, the `mine` process must be run before.",
        epilog="A file containing all results can be found in the `results/<detector>/Results.txt` file. ")  # type: ArgumentParser
    mine_parser.add_argument('detector', help="the results of this detector will be evaluated",
                             choices=available_detectors)
