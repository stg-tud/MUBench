import argparse
from argparse import ArgumentParser, HelpFormatter, ArgumentTypeError
from operator import attrgetter
from os.path import join, abspath, dirname
from typing import List, Any

import os

from data.detectors import get_available_detector_ids
from tasks.implementations import stats
from utils.dataset_util import get_available_dataset_ids
from utils.io import read_yaml

MUBENCH_ROOT_PATH = abspath(join(dirname(abspath(__file__)), os.pardir, os.pardir))
__DATA_PATH = join(MUBENCH_ROOT_PATH, "data")
__CHECKOUTS_PATH = join(MUBENCH_ROOT_PATH, "checkouts")
__COMPILES_PATH = __CHECKOUTS_PATH
__FINDINGS_PATH = join(MUBENCH_ROOT_PATH, "findings")
__DATASETS_FILE_PATH = join(MUBENCH_ROOT_PATH, 'data', 'datasets.yml')
__DETECTORS_PATH = join(MUBENCH_ROOT_PATH, "detectors")


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


class CaseInsensitiveChoices(list):
    def __init__(self, iterable):
        super().__init__(iterable)

    def __contains__(self, other):
        return any([element for element in self if element.lower() == other.lower()])


def get_config(args: List[str]) -> Any:
    available_detectors = get_available_detector_ids(__DETECTORS_PATH)
    available_scripts = stats.get_available_calculator_names()
    available_datasets = get_available_dataset_ids(__DATASETS_FILE_PATH)
    parser = _get_command_line_parser(available_detectors, available_scripts, available_datasets)

    # remove first arg which always contains the script name
    args = args[1:]

    # add an invalid mode if no mode was given
    if not args:
        args.append("")

    return parser.parse_args(args)


def _get_command_line_parser(available_detectors: List[str], available_scripts: List[str],
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
        help="MUBench provides several tasks. "
             "Run `./mubench <task> -h` for details.",
        dest='task')

    parser.add_argument('--use-tmp-wrkdir', dest='use_tmp_wrkdir', default=__get_default('use-tmp-wrkdir', False),
                        help=argparse.SUPPRESS, action='store_true')
    parser.add_argument('--data-path', dest='data_path', default=__get_default('data-path', __DATA_PATH),
                        help=argparse.SUPPRESS)
    parser.add_argument('--checkouts-path', dest='checkouts_path',
                        default=__get_default('checkouts-path', __CHECKOUTS_PATH), help=argparse.SUPPRESS)
    parser.add_argument('--compiles-path', dest='compiles_path', default=__get_default('compiles-path', __COMPILES_PATH),
                        help=argparse.SUPPRESS)
    parser.add_argument('--findings-path', dest='findings_path', default=__get_default('findings-path', __FINDINGS_PATH),
                        help=argparse.SUPPRESS)
    parser.add_argument('--datasets-file-path', dest='datasets_file_path',
                        default=__get_default('datasets-file-path', __DATASETS_FILE_PATH), help=argparse.SUPPRESS)
    parser.add_argument('--detectors-path', dest='detectors_path',
                        default=__get_default('detectors-path', __DETECTORS_PATH), help=argparse.SUPPRESS)

    __add_check_requirements_subprocess(subparsers)
    __add_info_subprocess(available_datasets, subparsers)
    __add_checkout_subprocess(available_datasets, subparsers)
    __add_compile_subprocess(available_datasets, subparsers)
    __add_run_subprocess(available_detectors, available_datasets, subparsers)
    __add_publish_subprocess(available_detectors, available_datasets, subparsers)
    __add_stats_subprocess(available_scripts, available_datasets, subparsers)
    __add_check_dataset_subprocess(available_datasets, subparsers)

    return parser


try:
    __default_config = read_yaml("./default.config")
except FileNotFoundError:
    __default_config = None


def __get_default(parameter: str, default):
    if __default_config is not None and parameter in __default_config:
        return __default_config[parameter]
    return default


def __add_check_requirements_subprocess(subparsers) -> None:
    subparsers.add_parser('check', formatter_class=SortingHelpFormatter,
                          help="Check whether the environment meets the prerequisites to run MUBench.",
                          description="Check whether the environment meets the prerequisites to run MUBench.")


def __add_check_dataset_subprocess(available_datasets: List[str], subparsers) -> None:
    dataset_check_parser = subparsers.add_parser('dataset-check', formatter_class=SortingHelpFormatter,
                                                 help="Check the consistency of MUBench's dataset.",
                                                 description="Check the consistency of MUBench's dataset. "
                                                             "Checks misuse locations only in project versions that "
                                                             "are already checked out. Manually run `checkout` first, "
                                                             "to ensure this check.")
    __setup_filter_arguments(dataset_check_parser, available_datasets)


def __add_info_subprocess(available_datasets: List[str], subparsers) -> None:
    parser = subparsers.add_parser('info', formatter_class=SortingHelpFormatter,
                                   help="Show info about projects, project versions, and misuses in MUBench.",
                                   description="Show info about projects, project versions, and misuses in MUBench.")
    __setup_filter_arguments(parser, available_datasets)


def __add_stats_subprocess(available_scripts: List[str], available_datasets: List[str], subparsers) -> None:
    stats_parser = subparsers.add_parser('stats', formatter_class=SortingHelpFormatter,
                                         description="Print statistics on the MUBench dataset.",
                                         help="Print statistics on the MUBench dataset.")
    stats_parser.add_argument('script', help="MUBench provides several statistics.",
                              choices=available_scripts)
    __setup_filter_arguments(stats_parser, available_datasets)


def __add_checkout_subprocess(available_datasets: List[str], subparsers) -> None:
    checkout_parser = subparsers.add_parser('checkout', formatter_class=SortingHelpFormatter,
                                            help="Checkout project versions.",
                                            description="Checkout project versions with known misuses in the MUBench "
                                                        "dataset. "
                                                        "Requires internet connection to access respective code "
                                                        "repositories. "
                                                        "Places checkouts in `checkouts`.")
    __setup_filter_arguments(checkout_parser, available_datasets)
    __setup_checkout_arguments(checkout_parser)


def __add_compile_subprocess(available_datasets: List[str], subparsers) -> None:
    compile_parser = subparsers.add_parser('compile', formatter_class=SortingHelpFormatter,
                                           help="Compile project versions. "
                                                "Runs `checkout`, if necessary.",
                                           description="Compile project versions and correct usages (patterns) "
                                                       "corresponding to the known misuses in these versions. "
                                                       "Runs `checkout`, if necessary. "
                                                       "Places compile results in `checkouts`.")
    __setup_filter_arguments(compile_parser, available_datasets)
    __setup_compile_arguments(compile_parser)
    __setup_checkout_arguments(compile_parser)


def __add_run_subprocess(available_detectors: List[str], available_datasets: List[str], subparsers) -> None:
    run_parser = subparsers.add_parser('run', formatter_class=SortingHelpFormatter,
                                       help="Run an experiment. "
                                            "Runs `checkout` and `compile`, if necessary.",
                                       description="Run an experiment, i.e., run a detector with the "
                                                   "experiment-specific inputs. "
                                                   "Runs `checkout` and `compile`, if necessary."
                                                   "Stores detector findings in `findings`.")

    run_subparsers = run_parser.add_subparsers(dest='sub_task',
                                               help="MUBench supports several experiments. "
                                                    "Run `./mubench run <experiment> -h` for details.")
    run_subparsers.required = True

    __add_run_ex1_subprocess(available_detectors, available_datasets, run_subparsers)
    __add_run_ex2_subprocess(available_detectors, available_datasets, run_subparsers)
    __add_run_ex3_subprocess(available_detectors, available_datasets, run_subparsers)


def __add_run_ex1_subprocess(available_detectors: List[str], available_datasets: List[str], subparsers) -> None:
    experiment_parser = subparsers.add_parser("ex1", formatter_class=SortingHelpFormatter,
                                              help="Experiment 1: Run a detector on misuses, providing respective "
                                                   "correct usages (patterns), to measure its recall.",
                                              description="Experiment 1: Run a detector on misuses, providing "
                                                          "respective correct usages (patterns), to measure the recall "
                                                          "of the detector's detection strategy in isolation.")
    __setup_filter_arguments(experiment_parser, available_datasets)
    __setup_checkout_arguments(experiment_parser)
    __setup_compile_arguments(experiment_parser)
    __setup_run_arguments(experiment_parser, available_detectors)


def __add_run_ex2_subprocess(available_detectors: List[str], available_datasets: List[str], subparsers) -> None:
    experiment_parser = subparsers.add_parser("ex2", formatter_class=SortingHelpFormatter,
                                              help="Experiment 2: Run a detector on project versions, to measure its "
                                                   "precision.",
                                              description="Experiment 2: Run a detector on project versions, to "
                                                          "measure the precision of the entire detector (mining and "
                                                          "detection).")
    __setup_filter_arguments(experiment_parser, available_datasets)
    __setup_checkout_arguments(experiment_parser)
    __setup_compile_arguments(experiment_parser)
    __setup_run_arguments(experiment_parser, available_detectors)
    __setup_publish_precision_arguments(experiment_parser)


def __add_run_ex3_subprocess(available_detectors: List[str], available_datasets: List[str], subparsers) -> None:
    experiment_parser = subparsers.add_parser("ex3", formatter_class=SortingHelpFormatter,
                                              help="Experiment 3: Run a detector on project versions, to measure its "
                                                   "recall.",
                                              description="Experiment 3: Run a detector on project versions, to "
                                                          "measure the recall of the entire detector (mining and "
                                                          "detection).")
    __setup_filter_arguments(experiment_parser, available_datasets)
    __setup_checkout_arguments(experiment_parser)
    __setup_compile_arguments(experiment_parser)
    __setup_run_arguments(experiment_parser, available_detectors)


def __add_publish_subprocess(available_detectors: List[str], available_datasets: List[str], subparsers) -> None:
    publish_parser = subparsers.add_parser('publish', formatter_class=SortingHelpFormatter,
                                           help="Publish data to a review site. "
                                                "Runs `checkout`, `compile`, and `run` , if necessary.",
                                           description="Publish data to a review site. "
                                                       "Runs `checkout`, `compile`, and `run` , if necessary.")

    publish_subparsers = publish_parser.add_subparsers(dest='sub_task',
                                                       help="MUBench provides several publish tasks. "
                                                            "Run `./mubench publish <task> -h` for details.")
    publish_subparsers.required = True

    __add_publish_metadata(available_datasets, publish_subparsers)
    __add_publish_ex1_subprocess(available_detectors, available_datasets, publish_subparsers)
    __add_publish_ex2_subprocess(available_detectors, available_datasets, publish_subparsers)
    __add_publish_ex3_subprocess(available_detectors, available_datasets, publish_subparsers)


def __add_publish_metadata(available_datasets, publish_subparsers) -> None:
    publish_metadata_parser = publish_subparsers.add_parser('metadata', formatter_class=SortingHelpFormatter,
                                                            help="Publish misuse metadata.",
                                                            description="Publish misuse metadata. "
                                                                        "This metadata is displayed on the review site "
                                                                        "for the recall experiments, to assist "
                                                                        "reviewers in deciding whether a potential hit "
                                                                        "corresponds to the known misuse from the "
                                                                        "MUBench dataset.")
    __setup_filter_arguments(publish_metadata_parser, available_datasets)
    __setup_checkout_arguments(publish_metadata_parser)
    __setup_publish_arguments(publish_metadata_parser)


def __add_publish_ex1_subprocess(available_detectors: List[str], available_datasets: List[str], subparsers) -> None:
    experiment_parser = subparsers.add_parser("ex1", formatter_class=SortingHelpFormatter,
                                              help="Experiment 1: Publish potential hits for known misuses to assess "
                                                   "a detector's recall when it uses provided correct usages "
                                                   "(patterns).",
                                              description="Experiment 1: Publish potential hits for known misuses, "
                                                          "i.e., detector findings in the same file and method as a "
                                                          "known misuse, to assess the detector's recall. "
                                                          "Considers the detector's findings when run on misuses, "
                                                          "providing respective correct usages (patterns). "
                                                          "This measures the recall of the detector's detection "
                                                          "strategy in isolation.")
    __setup_filter_arguments(experiment_parser, available_datasets)
    __setup_checkout_arguments(experiment_parser)
    __setup_compile_arguments(experiment_parser)
    __setup_run_arguments(experiment_parser, available_detectors)
    __setup_publish_arguments(experiment_parser)


def __add_publish_ex2_subprocess(available_detectors: List[str], available_datasets: List[str], subparsers) -> None:
    experiment_parser = subparsers.add_parser("ex2", formatter_class=SortingHelpFormatter,
                                              help="Experiment 2: Publish top findings to assess a detector's "
                                                   "precision when it uses its own specifications/patterns.",
                                              description="Experiment 2: Publish top findings of a detector, to assess "
                                                          "its precision. Considers the detector's top findings when "
                                                          "run on individual project versions. "
                                                          "This measure the precision of the entire detector (both "
                                                          "mining and detection).")
    __setup_filter_arguments(experiment_parser, available_datasets)
    __setup_checkout_arguments(experiment_parser)
    __setup_compile_arguments(experiment_parser)
    __setup_run_arguments(experiment_parser, available_detectors)
    __setup_publish_arguments(experiment_parser)
    __setup_publish_precision_arguments(experiment_parser)


def __add_publish_ex3_subprocess(available_detectors: List[str], available_datasets: List[str],
                             subparsers) -> None:
    experiment_parser = subparsers.add_parser("ex3", formatter_class=SortingHelpFormatter,
                                              help="Experiment 3: Publish potential hits for known misuses to assess "
                                                   "a detector's recall when it uses its own specifications/patterns.",
                                              description="Experiment 3: Publish potential hits for known misuses, "
                                                          "i.e., detector findings in the same file and method as a "
                                                          "known misuse, to assess the detector's recall. "
                                                          "Considers the detector's finding when run on individual "
                                                          "project versions. "
                                                          "This measures the recall of the entire detector (both "
                                                          "mining and detection).")
    __setup_filter_arguments(experiment_parser, available_datasets)
    __setup_checkout_arguments(experiment_parser)
    __setup_compile_arguments(experiment_parser)
    __setup_run_arguments(experiment_parser, available_detectors)
    __setup_publish_arguments(experiment_parser)


def __setup_filter_arguments(parser: ArgumentParser, available_datasets: List[str]) -> None:
    parser.add_argument('--only', metavar='X', nargs='+', dest='white_list', default=__get_default('only', []),
                        help="process only projects or project versions whose names are given")
    parser.add_argument('--skip', metavar='Y', nargs='+', dest='black_list', default=__get_default('skip', []),
                        help="skip all projects or project versions whose names are given")
    parser.add_argument('--dataset', metavar='DATASET', dest='dataset', default=__get_default('dataset', None),
                        choices=available_datasets, help="process only misuses in the specified data set")


def __setup_checkout_arguments(parser: ArgumentParser) -> None:
    parser.add_argument('--force-checkout', dest='force_checkout', action='store_true',
                        default=__get_default('force-checkout', False),
                        help="force a clean checkout, deleting any existing files")


def __setup_compile_arguments(parser: ArgumentParser) -> None:
    parser.add_argument('--force-compile', dest='force_compile', action='store_true',
                        default=__get_default('force-compile', False),
                        help="force a clean compilation")


def __setup_run_arguments(parser: ArgumentParser, available_detectors: List[str]) -> None:
    parser.add_argument('detector', help="the detector whose findings to evaluate",
                        choices=available_detectors)
    parser.add_argument('--force-detect', dest='force_detect', action='store_true',
                        default=__get_default('force-detect', False),
                        help="force a clean detection, deleting the any previous findings")
    parser.add_argument('--timeout', type=int, default=__get_default('timeout', None), metavar='s',
                        help="abort detection after the provided number of seconds")
    parser.add_argument('--java-options', metavar='option', nargs='+', dest='java_options',
                        default=__get_default('java-options', []),
                        help="pass options to the java subprocess running the detector "
                             "(example: `--java-options Xmx4G` runs `java -Xmx4G`)")
    parser.add_argument('--tag', dest='requested_release', default=__get_default('requested_release', None),
                        metavar='rel', help="use a specific detector release by tag")


def __setup_publish_arguments(parser: ArgumentParser) -> None:
    default_review_site = __get_default('review-site', None)
    parser.add_argument("-s", "--review-site", required=(not default_review_site), metavar="URL",
                        dest="review_site_url", default=default_review_site, help="use the specified review site")
    parser.add_argument("-u", "--username", metavar="USER", dest="review_site_user",
                        default=__get_default('username', None),
                        help="use the specified user to authenticate with the review site."
                             " If a user is provided, but no password,"
                             " you will be prompted for the password before publication.")
    parser.add_argument("-p", "--password", metavar="PASS", dest="review_site_password",
                        default=__get_default('password', None),
                        help="use the specified password for authenticating as the specified user."
                             " If a user is provided, but no password,"
                             " you will be prompted for the password before publication.")


def __setup_publish_precision_arguments(parser: ArgumentParser) -> None:
    def upload_limit(x):
        limit = int(x)
        if limit < 1:
            raise ArgumentTypeError("invalid value: {}, must be positive".format(limit))
        return limit

    parser.add_argument('--limit', type=upload_limit, default=__get_default('limit', 50), metavar='n',
                        dest="limit",
                        help="publish only the top-n findings. Defaults to 50")
