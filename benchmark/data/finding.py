from typing import Dict, List

from benchmark.data.misuse import Misuse
from benchmark.utils.java_utils import exec_util


class Snippet:
    def __init__(self, code: str, first_line: int):
        self.code = code
        self.first_line = first_line


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
        return self["file"]

    def __is_match_by_method(self, misuse_method, method_name_only: bool = False):
        finding_method = self.__method()

        if method_name_only:
            finding_method = finding_method.split("(")[0]

        # If detector reports only method names, this ensures we don't match prefixes of method names
        if "(" not in finding_method:
            finding_method += "("

        return finding_method in misuse_method

    def __method(self):
        return self["method"] if "method" in self else ""

    def get_snippet(self):
        code = exec_util("MethodExtractor", "\"{}\" \"{}\"".format(self.__file(), self.__method()))

        return Snippet(code, -1)


class SpecializedFinding(Finding):
    def __init__(self, data: Dict[str, str], files: List[str] = None):
        super().__init__(data)
        self.files = files or []
