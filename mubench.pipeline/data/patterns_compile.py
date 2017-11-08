from os.path import join, isdir
from typing import Set

from data.pattern import Pattern
from utils.io import remove_tree


class PatternsCompile:
    PATTERN_SOURCE_DIR = "patterns-src"
    PATTERN_CLASSES_DIR = "patterns-classes"
    MISUSE_SOURCE_DIR = "misuse-src"
    MISUSE_CLASSES_DIR = "misuse-classes"

    def __init__(self, base_path: str, patterns: Set[Pattern]):
        self.base_path = base_path
        self.patterns = patterns

        self.pattern_sources_path = join(self.base_path, PatternsCompile.PATTERN_SOURCE_DIR)
        self.pattern_classes_path = join(self.base_path, PatternsCompile.PATTERN_CLASSES_DIR)
        self.misuse_source_path = join(self.base_path, PatternsCompile.MISUSE_SOURCE_DIR)
        self.misuse_classes_path = join(self.base_path, PatternsCompile.MISUSE_CLASSES_DIR)

    def needs_copy_sources(self):
        return self.patterns and not isdir(self.get_source_path())

    def needs_compile(self):
        return self.patterns and not isdir(self.get_classes_path())

    def get_source_path(self):
        return self.pattern_sources_path

    def get_classes_path(self):
        return self.pattern_classes_path

    def delete(self):
        remove_tree(self.pattern_sources_path)
        remove_tree(self.pattern_classes_path)
        remove_tree(self.misuse_source_path)
        remove_tree(self.misuse_classes_path)
