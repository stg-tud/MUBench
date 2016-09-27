from distutils.file_util import copy_file
from os import makedirs
from os.path import exists, join, dirname, basename, splitext


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

    @property
    def orig_dir(self):
        return dirname(self.path)

    @property
    def file_name(self):
        return self.pattern_path

    @property
    def file_name_without_extension(self):
        return splitext(self.file_name)[0]

    def copy(self, destination: str):
        new_pattern = Pattern(destination, self.file_name)
        makedirs(new_pattern.orig_dir, exist_ok=True)
        copy_file(self.path, new_pattern.path)

    def _get_destination_file(self, destination: str) -> str:
        return join(destination, self.file_name)


class NoPatternFileError(FileNotFoundError):
    pass
