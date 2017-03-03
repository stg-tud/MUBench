import logging


class IndentFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, rec):
        logger_name = rec.name
        logger_level = 0
        if logger_name != "root":
            logger_level = logger_name.count('.') + 1
        rec.indent = "    " * logger_level
        out = logging.Formatter.format(self, rec)
        out = out.replace("\n", "\n" + rec.indent)
        del rec.indent
        return out
