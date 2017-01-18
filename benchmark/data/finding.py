from typing import Dict, List

import re

from os.path import join

from benchmark.data.misuse import Misuse
from benchmark.utils.java_utils import exec_util
from benchmark.utils.shell import CommandFailedError


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


class Finding(Dict[str, str]):
    def __init__(self, data: Dict[str, str]):
        super().__init__()
        self.update(data)

    def is_potential_hit(self, misuse: Misuse, method_name_only: bool = False):
        return self.__is_match_by_file(misuse.location.file) and \
               self.__is_match_by_method(misuse.location.method, method_name_only)

    def __is_match_by_file(self, misuse_file: str):
        finding_file = self.__file()

        # If file is an inner class "Outer$Inner.class", the source file is "Outer.java".
        if "$" in finding_file:
            finding_file = finding_file.split("$", 1)[0] + ".java"

        # If file is a class file "A.class", the source file is "A.java".
        if finding_file.endswith(".class"):
            finding_file = finding_file[:-5] + "java"

        return finding_file.endswith(misuse_file)

    def __file(self):
        return self.get("file", "")

    def __is_match_by_method(self, misuse_method, method_name_only: bool = False):
        finding_method = self.__method()

        if method_name_only:
            finding_method = finding_method.split("(")[0]

        # If detector reports only method names, this ensures we don't match prefixes of method names
        if "(" not in finding_method:
            finding_method += "("

        return finding_method in misuse_method

    def __method(self):
        return self.get("method", "")

    def get_snippets(self, source_base_path: str) -> List[Snippet]:
        snippets = []

        try:
            if self.__file() and self.__method():
                # output comes as:
                #
                #   <first-line number>:<declaring type>:<code>
                #   ===
                #   <first-line number>:<declaring type>:<code>
                #
                target_file = join(source_base_path, self.__file())
                output = exec_util("MethodExtractor", "\"{}\" \"{}\"".format(target_file, self.__method()))

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


class SpecializedFinding(Finding):
    def __init__(self, data: Dict[str, str], files: List[str] = None):
        super().__init__(data)
        self.files = files or []
