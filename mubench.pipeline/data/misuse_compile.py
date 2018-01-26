from os.path import join, isdir, exists
from typing import Set

from data.pattern import Pattern
from utils.io import remove_tree, write_yaml, read_yaml


class MisuseCompile:
    PATTERN_SOURCE_DIR = "patterns-src"
    PATTERN_CLASSES_DIR = "patterns-classes"
    MISUSE_SOURCE_DIR = "misuse-src"
    MISUSE_CLASSES_DIR = "misuse-classes"
    __MISUSE_COMPILE_FILE = "misuse_compile.yml"
    __TIMESTAMP_KEY = "timestamp"
    __DEFAULT_TIMESTAMP = 0

    def __init__(self, base_path: str, patterns: Set[Pattern]):
        self.base_path = base_path
        self.patterns = patterns

        self.pattern_sources_path = join(self.base_path, MisuseCompile.PATTERN_SOURCE_DIR)
        self.pattern_classes_path = join(self.base_path, MisuseCompile.PATTERN_CLASSES_DIR)
        self.misuse_source_path = join(self.base_path, MisuseCompile.MISUSE_SOURCE_DIR)
        self.misuse_classes_path = join(self.base_path, MisuseCompile.MISUSE_CLASSES_DIR)

        self._misuse_compile_file = join(self.base_path, MisuseCompile.__MISUSE_COMPILE_FILE)

    def needs_copy_sources(self):
        return self.patterns and not isdir(self.pattern_sources_path)

    def needs_compile(self):
        return self.patterns and not isdir(self.pattern_classes_path)

    @property
    def timestamp(self):
        timestamp = self.__DEFAULT_TIMESTAMP

        if exists(self._misuse_compile_file):
            compile_info = read_yaml(self._misuse_compile_file)
            timestamp = compile_info.get(self.__TIMESTAMP_KEY, self.__DEFAULT_TIMESTAMP)

        return timestamp

    def save(self, timestamp: int):
        misuse_compile_info = {self.__TIMESTAMP_KEY: timestamp}
        write_yaml(misuse_compile_info, self._misuse_compile_file)

    def delete(self):
        remove_tree(self.pattern_sources_path)
        remove_tree(self.pattern_classes_path)
        remove_tree(self.misuse_source_path)
        remove_tree(self.misuse_classes_path)
        remove_tree(self._misuse_compile_file)
