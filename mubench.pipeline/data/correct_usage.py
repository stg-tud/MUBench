from os.path import join, dirname, basename, splitext


class CorrectUsage:
    def __init__(self, basepath: str, relative_correct_usage_path: str):
        self.basepath = basepath
        self.__relative_correct_usage_path = relative_correct_usage_path
        self.path = join(basepath, relative_correct_usage_path)
        self.orig_dir = dirname(self.path)
        self.name = splitext(basename(self.__relative_correct_usage_path))[0]

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return isinstance(other, CorrectUsage) and self.path == other.path

    def __str__(self):
        return self.path

    @property
    def relative_path_without_extension(self):
        return splitext(self.__relative_correct_usage_path)[0]

    def _get_destination_file(self, destination: str) -> str:
        return join(destination, self.__relative_correct_usage_path)


class NoPatternFileError(FileNotFoundError):
    pass
