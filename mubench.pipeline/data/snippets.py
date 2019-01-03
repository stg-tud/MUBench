import os
import re
from os.path import join
from typing import List

from utils import io
from utils.java_utils import exec_util


def get_snippets(source_base_paths: List[str], file: str, method: str, target_line_number: int = -1) -> List['Snippet']:
    snippets = []

    for source_base_path in source_base_paths:
        try:
            snippets.extend(__get_snippets(source_base_path, file, method, target_line_number))
        except SnippetUnavailableException:
            continue

    if not snippets:
        raise SnippetUnavailableException(file, method)

    return snippets


def __get_snippets(source_base_path: str, file: str, method: str, target_line_number: int) -> List['Snippet']:
    target_file = join(source_base_path, file)
    snippets = []
    snippets_with_matching_line_number = []
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
                    first_line, class_name, code = method.split(":", 2)
                    first_line = int(first_line)
                    snippet = Snippet("""class {} {{\n{}\n}}""".format(class_name, code), first_line - 1)
                    snippets.append(snippet)

                    last_line = first_line + code.count("\n")
                    if first_line <= target_line_number <= last_line:
                        snippets_with_matching_line_number.append(snippet)
        elif file and os.path.exists(target_file):
            snippets.append(Snippet(io.safe_read(target_file), 1))

    except Exception as e:
        raise SnippetUnavailableException(target_file, method, e)
    return snippets_with_matching_line_number if snippets_with_matching_line_number else snippets


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
    def __init__(self, file: str, method: str, exception: Exception = None):
        self.file = file
        self.method = method
        self.exception = exception if exception else "no matches"

    def __str__(self):
        return "Could not extract snippet for '{}' from '{}': {}".format(self.method, self.file, self.exception)
