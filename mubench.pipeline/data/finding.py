from typing import Dict, List

from data.misuse import Misuse
from data.snippets import get_snippets, Snippet


class Finding(Dict[str, str]):
    def __init__(self, data: Dict[str, str]):
        super().__init__(data)

    def is_potential_hit(self, misuse: Misuse, source_base_paths: List[str], method_name_only: bool = False):
        for file_match in [location for location in misuse.locations if self.__is_match_by_file(location.file)]:
            if self.__is_match_by_method(file_match.method, method_name_only) and \
               self.__is_match_by_line(misuse.get_snippets(source_base_paths)):
                return True

        return False

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

        return misuse_method.startswith(finding_method)

    def __is_match_by_line(self, snippets: List[Snippet]):
        if self.__startline() < 0:
            return True

        for snippet in snippets:
            snippet_last_line_number = snippet.first_line_number + snippet.code.count("\n")
            if snippet.first_line_number < self.__startline() < snippet_last_line_number:
                return True

        return False

    def __method(self):
        return self.get("method", "")

    def __startline(self):
        return self.get("startline", -1)

    def get_snippets(self, source_base_paths: List[str]) -> List[Snippet]:
        return get_snippets(source_base_paths, self.__file(), self.__method(), self.__startline())
