import shutil
from os import makedirs, listdir
from os.path import join, isdir, isfile, dirname, exists
from typing import Set

from benchmark.data.build_config import BuildConfig
from benchmark.data.pattern import Pattern
from benchmark.utils.io import remove_tree, copy_tree


class ProjectCompile:
    ORIGINAL_SOURCE_DIR = "original-src"
    ORIGINAL_CLASSES_DIR = "original-classes"
    PATTERN_SOURCE_DIR = "patterns-src"
    PATTERN_CLASSES_DIR = "patterns-classes"

    def __init__(self, checkout_dir: str, base_path: str, build_config: BuildConfig, patterns: Set[Pattern]):
        self.__checkout_dir = checkout_dir
        self.__base_path = base_path
        self.__build_config = build_config if build_config else BuildConfig("", [], "")
        self.__patterns = patterns
        self.__build_path = join(self.__base_path, "build")
        self.original_sources_path = join(self.__base_path, ProjectCompile.ORIGINAL_SOURCE_DIR)
        self.original_classes_path = join(self.__base_path, ProjectCompile.ORIGINAL_CLASSES_DIR)
        self.pattern_sources_path = join(self.__base_path, ProjectCompile.PATTERN_SOURCE_DIR)
        self.pattern_classes_path = join(self.__base_path, ProjectCompile.PATTERN_CLASSES_DIR)

    def exists_copy_of_original_source(self):
        return isdir(self.original_sources_path)

    def copy_original_sources(self):
        project_source_path = join(self.__checkout_dir, self.__build_config.src)
        makedirs(self.original_sources_path, exist_ok=True)
        self._copy(project_source_path, self.original_sources_path)

    def delete_original_source(self):
        remove_tree(self.original_sources_path)

    def exists_copy_of_pattern_sources(self):
        return isdir(self.pattern_sources_path)

    def copy_pattern_sources(self, pattern_frequency: int):
        for pattern in self.__patterns:
            pattern.duplicate(self.pattern_sources_path, pattern_frequency)

    def is_original_compile(self) -> bool:
        return False

    def compile_original(self):
        pass

    def is_patterns_compiled(self) -> bool:
        return False

    def compile_patterns(self):
        pass

    def delete(self):
        remove_tree(self.original_sources_path)
        remove_tree(self.original_classes_path)
        remove_tree(self.pattern_sources_path)
        remove_tree(self.pattern_classes_path)
        remove_tree(self.__build_path)

    @staticmethod
    def _copy(src, dst):
        if isdir(dst):
            remove_tree(dst)

        if isdir(src):
            copy_tree(src, dst)
        elif isfile(src):
            makedirs(dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
        else:
            raise FileNotFoundError("no such file or directory {}".format(src))