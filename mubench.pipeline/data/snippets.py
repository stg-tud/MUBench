import re
from os.path import join

from utils.java_utils import exec_util
from utils.shell import CommandFailedError


def get_snippets(source_base_path, file, method):
    snippets = []
    try:
        if file and method:
            # output comes as:
            #
            #   <first-line number>:<declaring type>:<code>
            #   ===
            #   <first-line number>:<declaring type>:<code>
            #
            target_file = join(source_base_path, file)
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

    except CommandFailedError as e:
        snippets.append(Snippet(str(e), 1))
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
