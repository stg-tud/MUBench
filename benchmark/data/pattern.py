from distutils.file_util import copy_file
from fileinput import FileInput
from os import makedirs
from os.path import exists, join, splitext, dirname, basename
from typing import Set


class Pattern:
    def __init__(self, basepath: str, pattern_path: str):
        self.basepath = basepath
        self.pattern_path = pattern_path
        self.path = join(basepath, pattern_path)

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return isinstance(other, Pattern) and self.path == other.path

    def __str__(self):
        return self.path

    def is_valid(self) -> bool:
        if not self.path.endswith(".java") or not exists(self.path):
            raise NoPatternFileError("Pattern file is invalid!")

    @property
    def orig_dir(self):
        return dirname(self.path)

    @property
    def file_name(self):
        return splitext(self.pattern_path)[0]

    @property
    def class_name(self):
        return basename(self.file_name)

    @property
    def file_extension(self):
        return splitext(self.path)[1]

    def duplicate(self, destination: str, times: int):
        duplicates = set()
        for i in range(times):
            duplicates.add(self.copy(destination, str(i)))
        return duplicates

    def copy(self, destination: str, suffix: str="") -> str:
        new_pattern_path = self.file_name + suffix + self.file_extension
        new_pattern = Pattern(destination, new_pattern_path)

        makedirs(new_pattern.orig_dir, exist_ok=True)
        copy_file(self.path, new_pattern.path)

        self._replace_class_name(new_pattern.path, suffix)

        return new_pattern

    def _get_destination_file(self, destination: str, i: int) -> str:
        return join(destination, self.file_name + str(i) + self.file_extension)

    def _replace_class_name(self, copied_file: str, suffix: str) -> None:
        with FileInput(copied_file, inplace=True) as file:
            for line in file:
                # FileInput inplace redirects stdout to the file
                print(line.replace(self.class_name, self.class_name + suffix), end='')


class NoPatternFileError(FileNotFoundError):
    pass
