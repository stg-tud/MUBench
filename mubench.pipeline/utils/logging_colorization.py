import logging
import platform


def __add_emit_without_colors(fn):
    def __emit_without_color(*args):
        args[0].levelcolor = ''
        args[0].resetcolor = ''

        return fn(*args)

    return __emit_without_color


def __add_emit_with_ansi_colors(fn):
    def __emit_with_ansi_color(*args):
        __RED = '\x1b[31m'
        __YELLOW = '\x1b[33m'
        __GREEN = '\x1b[32m'
        __NO_COLOR = '\x1b[0m'

        level = args[0].levelno
        if level == logging.CRITICAL:
            color = __RED
        elif level == logging.ERROR:
            color = __RED
        elif level == logging.WARNING:
            color = __YELLOW
        elif level == logging.INFO:
            color = __GREEN
        else:  # logging.DEBUG
            color = __NO_COLOR

        args[0].levelcolor = color
        args[0].resetcolor = __NO_COLOR

        return fn(*args)

    return __emit_with_ansi_color


def register_levelcolor_replacement_field(handler: logging.StreamHandler):
    if platform.system() == "Windows":
        handler.emit = __add_emit_without_colors(handler.emit)
    else:
        handler.emit = __add_emit_with_ansi_colors(handler.emit)
