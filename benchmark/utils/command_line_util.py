from argparse import ArgumentParser

from typing import List, Any


def get_command_line_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="MUBenchmark",
                            description="A benchmark for usage model miners and misuse detectors",
                            epilog="See the README.md for further information")

    subparsers = parser.add_subparsers(help="MUBenchmark Modes", dest='mode')

    subparsers.add_parser('check', help="checks if all prerequisites are met")  # type: ArgumentParser

    subparsers.add_parser('checkout', help="pre-loads projects")  # type: ArgumentParser

    mine_parser = subparsers.add_parser('mine', help="this mode is not yet implemented")  # type: ArgumentParser
    mine_parser.add_argument('miner', help="this option is not used yet")
    mine_parser.add_argument('--only', help="run only using data files which contain any of these strings",
                             metavar='X', nargs='+', dest='white_list', default=[""])
    mine_parser.add_argument('--ignore', help="don't run with data files which contain any of these strings",
                             metavar='Y', nargs='+', dest='black_list', default=[])
    mine_parser.add_argument('--timeout', type=int, default=None, metavar='s',
                             help="ignores the current case if the detector did not finish after this many seconds")

    evaluate_parser = subparsers.add_parser(
        'eval', help="runs the misuse detector and evaluates its output")  # type: ArgumentParser
    evaluate_parser.add_argument('detector', help="see the MUBench/detectors folder for a list of usable detectors")
    evaluate_parser.add_argument('--only', help="run only using data files which contain any of these strings",
                                 metavar='X', nargs='+', dest='white_list', default=[""])
    evaluate_parser.add_argument('--ignore', help="don't run with data files which contain any of these strings",
                                 metavar='Y', nargs='+', dest='black_list', default=[])
    evaluate_parser.add_argument('--timeout', type=int, default=None, metavar='s',
                                 help="ignores the current case if the detector did not finish after this many seconds")

    return parser


def parse_args(args: List[str]) -> Any:
    parser = get_command_line_parser()

    # remove first arg which always contains the script name
    args = args[1:]

    # add an invalid mode if no mode was given
    if not args:
        args.append("")

    return parser.parse_args(args)
