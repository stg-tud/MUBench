import argparse
from argparse import ArgumentParser, HelpFormatter, ArgumentTypeError
from operator import attrgetter

from typing import List, Any
from utils.io import read_yaml


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


class CaseInsensitiveChoices(list):
    def __init__(self, iterable):
        super().__init__(iterable)

    def __contains__(self, other):
        return any([element for element in self if element.lower() == other.lower()])

try:
    config = read_yaml("./default.config")
except FileNotFoundError:
    config = None


def get_default(parameter: str, default):
    if config is not None and parameter in config:
        return config[parameter]
    return default


def get_command_line_parser(available_detectors: List[str], available_scripts: List[str],
                            available_datasets: List[str]) -> ArgumentParser:
    available_detectors = CaseInsensitiveChoices(available_detectors)
    available_scripts = CaseInsensitiveChoices(available_scripts)
    available_datasets = CaseInsensitiveChoices(available_datasets)

    parser = ArgumentParser(
        prog="./mubench",
        description="Run MUBench, the benchmark for API-misuse detectors.",
        epilog="For details, check out https://github.com/stg-tud/MUBench.",
        formatter_class=SortingHelpFormatter)

    subparsers = parser.add_subparsers(
        help="MUBench provides several tasks. Run `mubench <task> -h` for details.",
        dest='task')

    parser.add_argument('--windows-fix', dest='windows_fix', default=get_default('windows-fix', False),
                        help=argparse.SUPPRESS, action='store_true')

    __add_check_subprocess(subparsers)
    __add_info_subprocess(available_datasets, subparsers)
    __add_checkout_subprocess(available_datasets, subparsers)
    __add_compile_subprocess(available_datasets, subparsers)
    __add_detect_subprocess(available_detectors, available_datasets, subparsers)
    __add_publish_subprocess(available_detectors, available_datasets, subparsers)
    __add_stats_subprocess(available_scripts, available_datasets, subparsers)

    return parser


def parse_args(args: List[str], available_detectors: List[str], available_scripts: List[str],
               available_datasets: List[str]) -> Any:
    parser = get_command_line_parser(available_detectors, available_scripts, available_datasets)

    # remove first arg which always contains the script name
    args = args[1:]

    # add an invalid mode if no mode was given
    if not args:
        args.append("")

    return parser.parse_args(args)


def __add_check_subprocess(subparsers) -> None:
    subparsers.add_parser('check', formatter_class=SortingHelpFormatter,
                          help="Validate whether the environment meets the prerequisites to run MUBench.",
                          description="Validate whether the environment meets the prerequisites to run MUBench.")


def __add_info_subprocess(available_datasets: List[str], subparsers) -> None:
    parser = subparsers.add_parser('info', formatter_class=SortingHelpFormatter,
                                   help="Show info about projects, project versions, and misuses in MUBench.",
                                   description="Show info about projects, project versions, and misuses in MUBench.")
    __setup_misuse_filter_arguments(parser, available_datasets)


def __add_checkout_subprocess(available_datasets: List[str], subparsers) -> None:
    checkout_parser = subparsers.add_parser('checkout', formatter_class=SortingHelpFormatter,
                                            help="Clone the project versions with the misuses "
                                                 "from the MUBench dataset.",
                                            description="Clone the project versions with the misuses "
                                                        "from the MUBench dataset.",
                                            epilog="The clones will be created below `checkouts/`.")  # type: ArgumentParser
    __setup_misuse_filter_arguments(checkout_parser, available_datasets)
    __setup_checkout_arguments(checkout_parser)


def __add_compile_subprocess(available_datasets: List[str], subparsers) -> None:
    compile_parser = subparsers.add_parser('compile', formatter_class=SortingHelpFormatter,
                                           help="Compile the projects and the patterns. "
                                                "Run `checkout`, if necessary.",
                                           description="Compile the projects and patterns. "
                                                       "Run `checkout`, if necessary.",
                                           epilog="Compilation data is store below `checkouts/`.")  # type: ArgumentParser
    __setup_misuse_filter_arguments(compile_parser, available_datasets)
    __setup_compile_arguments(compile_parser)
    __setup_checkout_arguments(compile_parser)


def __add_detect_subprocess(available_detectors: List[str], available_datasets: List[str], subparsers) -> None:
    detect_parser = subparsers.add_parser('detect', formatter_class=SortingHelpFormatter,
                                          help="Run a detector on the checkouts. Run `compile`, if necessary. ",
                                          description="Run a detector on the checkouts. Run `compile`, if necessary. "
                                                      "Run `detect -h` to see a list of available detectors.",
                                          epilog="The findings are written to `findings/`.")  # type: ArgumentParser
    __setup_misuse_filter_arguments(detect_parser, available_datasets)
    __setup_detector_arguments(detect_parser, available_detectors)
    __setup_checkout_arguments(detect_parser)
    __setup_compile_arguments(detect_parser)


def __add_publish_subprocess(available_detectors: List[str], available_datasets: List[str], subparsers) -> None:
    publish_parser = subparsers.add_parser('publish', formatter_class=SortingHelpFormatter,
                                           help="Tasks to publish data to a review site.",
                                           description="Tasks to publish data to a review site.")  # type: ArgumentParser
    publish_subparsers = publish_parser.add_subparsers(
        help="MUBench provides multiple publishing tasks. Run `mubench publish <task> -h` for details. "
             "See https://github.com/stg-tud/MUBench#review-setup for details on how to setup a review site.",
        dest='publish_task')

    findings_parser = publish_subparsers.add_parser("findings", formatter_class=SortingHelpFormatter,
                                                    help="Publish detection findings to the review site. "
                                                         "Run `detect`, if necessary.",
                                                    description="Publish detection findings to the review site. "
                                                                "Run `detect`, if necessary.")  # type: ArgumentParser
    __setup_misuse_filter_arguments(findings_parser, available_datasets)
    __setup_detector_arguments(findings_parser, available_detectors)
    __setup_checkout_arguments(findings_parser)
    __setup_compile_arguments(findings_parser)
    __setup_publish_arguments(findings_parser)

    def upload_limit(x):
        limit = int(x)
        if limit < 1:
            raise ArgumentTypeError("invalid value: {}, must be positive".format(limit))
        return limit

    findings_parser.add_argument('--limit', type=upload_limit, default=get_default('limit', 50), metavar='n',
                                 dest="limit",
                                 help="publish only a specified number of potential hits. Defaults to 50")

    metadata_parser = publish_subparsers.add_parser("metadata", formatter_class=SortingHelpFormatter,
                                                    help="Publish misuse metadata to the review site. "
                                                         "Run `checkout`, if necessary.",
                                                    description="Publish misuse metadata to the review site. "
                                                                "Run `checkout`, if necessary.")  # type: ArgumentParser

    __setup_misuse_filter_arguments(metadata_parser, available_datasets)
    __setup_checkout_arguments(metadata_parser)
    __setup_publish_arguments(metadata_parser)


def __add_stats_subprocess(available_scripts: List[str], available_datasets: List[str], subparsers) -> None:
    stats_parser = subparsers.add_parser('stats', formatter_class=SortingHelpFormatter,
                                         description="Calculate statistics using the given script",
                                         help="Calculate statistics using the given script")  # type: ArgumentParser
    stats_parser.add_argument('script', help="the calculation strategy to use (case insensitive)",
                              choices=available_scripts)
    __setup_misuse_filter_arguments(stats_parser, available_datasets)


def __setup_misuse_filter_arguments(parser: ArgumentParser, available_datasets: List[str]):
    parser.add_argument('--only', metavar='X', nargs='+', dest='white_list', default=get_default('only', []),
                        help="process only projects or project versions whose names are given")
    parser.add_argument('--skip', metavar='Y', nargs='+', dest='black_list', default=get_default('skip', []),
                        help="skip all projects or project versions whose names are given")
    parser.add_argument('--dataset', metavar='DATASET', dest='dataset', default=get_default('dataset', None),
                        choices=available_datasets, help="process only misuses in the specified data set")


def __setup_checkout_arguments(parser: ArgumentParser):
    parser.add_argument('--force-checkout', dest='force_checkout', action='store_true',
                        default=get_default('force-checkout', False),
                        help="force a clean checkout, deleting any existing files")


def __setup_compile_arguments(parser: ArgumentParser):
    parser.add_argument('--force-compile', dest='force_compile', action='store_true',
                        default=get_default('force-compile', False),
                        help="force a clean compilation")


def __setup_detector_arguments(parser: ArgumentParser, available_detectors: List[str]) -> None:
    parser.add_argument('detector', help="the detector whose findings to evaluate",
                        choices=available_detectors)
    parser.add_argument('experiment', help="configures the detector for the experiment", type=int,
                        choices=[1, 2, 3])
    parser.add_argument('--force-detect', dest='force_detect', action='store_true',
                        default=get_default('force-detect', False),
                        help="force a clean detection, deleting the any previous findings")
    parser.add_argument('--timeout', type=int, default=get_default('timeout', None), metavar='s',
                        help="abort detection after the provided number of seconds")
    parser.add_argument('--java-options', metavar='option', nargs='+', dest='java_options',
                        default=get_default('java-options', []),
                        help="pass options to the java subprocess running the detector "
                             "(example: `--java-options Xmx4G` runs `java -Xmx4G`)")
    parser.add_argument('--tag', dest='requested_release', default=get_default('requested_release', None),
                        metavar='rel', help="use a specific detector release by tag")


def __setup_publish_arguments(parser: ArgumentParser) -> None:
    default_review_site = get_default('review-site', None)
    parser.add_argument("-s", "--review-site", required=(not default_review_site), metavar="URL",
                        dest="review_site_url", default=default_review_site, help="use the specified review site")
    parser.add_argument("-u", "--username", metavar="USER", dest="review_site_user",
                        default=get_default('username', None),
                        help="use the specified user to authenticate with the review site."
                             " If a user is provided, but no password,"
                             " you will be prompted for the password before publication.")
    parser.add_argument("-p", "--password", metavar="PASS", dest="review_site_password",
                        default=get_default('password', None),
                        help="use the specified password for authenticating as the specified user."
                             " If a user is provided, but no password,"
                             " you will be prompted for the password before publication.")
