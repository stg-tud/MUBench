from distutils.file_util import copy_file
from os import makedirs
from os.path import join, dirname, basename, splitext


class Pattern:
    def __init__(self, basepath: str, relative_pattern_path: str):
        self.basepath = basepath
        self.__relative_pattern_path = relative_pattern_path
        self.path = join(basepath, relative_pattern_path)
        self.orig_dir = dirname(self.path)
        self.name = splitext(basename(self.__relative_pattern_path))[0]

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return isinstance(other, Pattern) and self.path == other.path

    def __str__(self):
        return self.path

    @property
    def relative_path_without_extension(self):
        return splitext(self.__relative_pattern_path)[0]

    def copy(self, destination: str):
        new_pattern = Pattern(destination, self.__relative_pattern_path)
        makedirs(new_pattern.orig_dir, exist_ok=True)
        copy_file(self.path, new_pattern.path)

    def _get_destination_file(self, destination: str) -> str:
        return join(destination, self.__relative_pattern_path)


class NoPatternFileError(FileNotFoundError):
    pass
