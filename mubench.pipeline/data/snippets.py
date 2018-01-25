import os
import re
from os.path import join
from typing import List

from utils import io
from utils.java_utils import exec_util


def get_snippets(source_base_paths: List[str], file: str, method: str) -> List['Snippet']:
    snippets = []

    for source_base_path in source_base_paths:
        try:
            snippets.extend(__get_snippets(source_base_path, file, method))
        except SnippetUnavailableException:
            continue

    return snippets


def __get_snippets(source_base_path: str, file: str, method: str) -> List['Snippet']:
    target_file = join(source_base_path, file)
    snippets = []
    try:
        if file and method:
            # output comes as:
            #
            #   <first-line number>:<declaring type>:<code>
            #   ===
            #   <first-line number>:<declaring type>:<code>
            #
            output = exec_util("MethodExtractor", "\"{}\" \"{}\"".format(target_file, method))

            # if there's other preceding output, we need to strip it
            while output and not re.match("^[0-9]+:[^:\n]+:", output):
                output_lines = output.split("\n", 2)
                if len(output_lines) > 1:
                    output = output_lines[1]
                else:
                    output = ""

            if output:
                methods = output.split("\n===\n")
                for method in methods:
                    info = method.split(":", 2)
                    snippets.append(Snippet("""class {} {{\n{}\n}}""".format(info[1], info[2]), int(info[0]) - 1))
        elif file and os.path.exists(target_file):
            snippets.append(Snippet(io.safe_read(target_file), 1))

    except Exception as e:
        raise SnippetUnavailableException(target_file, e)
    return snippets


class Snippet:
    def __init__(self, code: str, first_line: int):
        self.code = code
        self.first_line_number = first_line

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return self.__dict__.__hash__()

    def __str__(self):
        return "{}:{}".format(self.first_line_number, self.code)


class SnippetUnavailableException(UserWarning):
    def __init__(self, file: str, exception: Exception):
        self.exception = exception
        self.file = file

    def __str__(self):
        return "Could not extract snippet from '{}': {}".format(self.file, self.exception)
