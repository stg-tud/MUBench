#!/usr/bin/env python
# encoding: utf-8
import logging


# inspired by: https://stackoverflow.com/a/1336640
def __add_coloring_to_emit_ansi(fn):
    RED = '\x1b[31m'
    YELLOW = '\x1b[33m'
    GREEN = '\x1b[32m'
    NO_COLOR = '\x1b[0m'

    # add methods we need to the class
    def new(*args):
        level = args[0].levelno
        if level == logging.CRITICAL:
            color = RED  # red
        elif level == logging.ERROR:
            color = RED  # red
        elif level == logging.WARNING:
            color = YELLOW  # yellow
        elif level == logging.INFO:
            color = GREEN  # green
        else:  # logging.DEBUG
            color = NO_COLOR  # normal

        args[0].levelcolor = color
        args[0].resetcolor = NO_COLOR
        return fn(*args)

    return new


def colorize(handler: logging.StreamHandler):
    handler.emit = __add_coloring_to_emit_ansi(handler.emit)
