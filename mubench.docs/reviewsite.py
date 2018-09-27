from argparse import ArgumentParser

import sys

parser = ArgumentParser(
    prog="reviewsite",
    description="Control a standalone review site within this container.")

subparsers = parser.add_subparsers(dest='task',
                                   help="You can execute the following tasks.")

subparsers.add_parser("start",
                      help="Fire up a review site. The site will spawn in the background "
                           "when you run this task in interactive mode.")
subparsers.add_parser("stop",
                      help="Shut down a review site running in the background. This works "
                           "in interactive mode only. Otherwise just kill the server "
                           "process using Ctrl+C.")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(2)

parser.parse_args(sys.argv[1:])
