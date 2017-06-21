from typing import Dict, List, Union

from data.misuse import Misuse
from data.snippets import get_snippets, Snippet


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

        return misuse_method.startswith(finding_method)

    def __method(self):
        return self.get("method", "")

    def get_snippets(self, source_base_path: str) -> List[Snippet]:
        return get_snippets(source_base_path, self.__file(), self.__method())

    def with_markdown(self) -> 'Finding':
        finding = Finding(dict())
        for key, value in self.items():
            finding[key] = _as_markdown(value)
        return finding


class SpecializedFinding(Finding):
    def __init__(self, data: Dict[str, str], files: List[str] = None):
        super().__init__(data)
        self.files = files or []


def _as_markdown(value: Union[List[str], Dict[str, str], str]) -> str:
    if isinstance(value, list):
        return __as_markdown_list(value)
    elif isinstance(value, dict):
        return __as_markdown_dict(value)
    elif isinstance(value, str):
        return value
    else:
        raise UnsupportedTypeError(value)


def __as_markdown_list(l: List[str]) -> str:
    markdown_list = []
    for item in l:
        try:
            markdown_list.append("* " + item)
        except TypeError:
            raise UnsupportedTypeError(item)
    return '\n'.join(markdown_list)


def __as_markdown_dict(d: Dict[str, str]) -> str:
    definition_list = []
    for key, value in d.items():
        try:
            definition_list.append("{}: \n{}".format(key, value))
        except TypeError:
            raise UnsupportedTypeError(value)
    return '\n'.join(definition_list)


class UnsupportedTypeError(TypeError):
    def __init__(self, obj):
        super().__init__("Unsupported type {} of {}".format(type(obj), repr(obj)))
