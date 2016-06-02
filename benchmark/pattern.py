from distutils.file_util import copy_file
from fileinput import FileInput
from os import makedirs
from os.path import exists, basename, join, splitext, dirname


class Pattern:
    def __init__(self, path: str):
        self.path = path

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return isinstance(other, Pattern) and self.path == other.path

    def __str__(self):
        return self.path

    def is_valid(self) -> bool:
        if not self.path.endswith(".java") or not exists(self.path):
            raise NoPatternFileError("Pattern file is not valid!")

    @property
    def orig_dir(self):
        return dirname(self.path)

    @property
    def file_name(self):
        return splitext(basename(self.path))[0]

    @property
    def class_name(self):
        return self.file_name

    @property
    def file_extension(self):
        return splitext(self.path)[1]

    def duplicate(self, destination: str, times: int) -> str:
        for i in range(times):
            self.copy(destination)
        return destination

    def copy(self, destination: str) -> str:
        makedirs(destination, exist_ok=True)

        i = 0
        while exists(self._get_destination_file(destination, i)):
            i += 1

        copied_file = self._get_destination_file(destination, i)
        copy_file(self.path, copied_file)

        self._replace_class_name(copied_file, i)

        return destination

    def _get_destination_file(self, destination: str, i: int) -> str:
        return join(destination, self.file_name + str(i) + self.file_extension)

    def _replace_class_name(self, copied_file: str, i: int) -> None:
        with FileInput(copied_file, inplace=True) as file:
            for line in file:
                if self.class_name in line:
                    # FileInput inplace redirects stdout to the file
                    print(line.replace(self.class_name, self.class_name + str(i)), end='')


class NoPatternFileError(FileNotFoundError):
    pass
