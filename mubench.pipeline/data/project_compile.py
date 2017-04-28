import os
from os.path import join, isdir
from typing import List

from data.misuse import Misuse


class ProjectCompile:
    ORIGINAL_SOURCE_DIR = "original-src"
    ORIGINAL_CLASSES_DIR = "original-classes"
    MISUSE_SOURCE_DIR = "misuse-src"
    MISUSE_CLASSES_DIR = "misuse-classes"
    PATTERN_SOURCE_DIR = "patterns-src"
    PATTERN_CLASSES_DIR = "patterns-classes"
    DEPENDENCY_DIR = "dependencies"

    def __init__(self, base_path: str, misuses: List[Misuse]):
        self.base_path = base_path
        self.misuses = misuses

        self.original_sources_path = join(self.base_path, ProjectCompile.ORIGINAL_SOURCE_DIR)
        self.original_classes_path = join(self.base_path, ProjectCompile.ORIGINAL_CLASSES_DIR)
        self.original_classpath = self.original_classes_path + ".jar"
        self.misuse_source_path = join(self.base_path, ProjectCompile.MISUSE_SOURCE_DIR)
        self.misuse_classes_path = join(self.base_path, ProjectCompile.MISUSE_CLASSES_DIR)
        self.pattern_sources_base_path = join(self.base_path, ProjectCompile.PATTERN_SOURCE_DIR)
        self.pattern_classes_base_path = join(self.base_path, ProjectCompile.PATTERN_CLASSES_DIR)
        self.dependencies_path = join(self.base_path, ProjectCompile.DEPENDENCY_DIR)

    def needs_copy_sources(self):
        if not isdir(self.original_sources_path):
            return True

        for misuse in self.misuses:
            if self.__needs_copy_pattern_sources(misuse):
                return True

        return False

    def __needs_copy_pattern_sources(self, misuse: Misuse):
        return misuse.patterns and not isdir(self.get_pattern_source_path(misuse))

    def needs_compile(self):
        if not isdir(self.original_classes_path):
            return True

        for misuse in self.misuses:
            if self.__needs_compile_patterns(misuse):
                return True

        return False

    def __needs_compile_patterns(self, misuse: Misuse):
        return misuse.patterns and not isdir(self.get_pattern_classes_path(misuse))

    def get_pattern_source_path(self, misuse: Misuse):
        return join(self.pattern_sources_base_path, misuse.misuse_id)

    def get_pattern_classes_path(self, misuse: Misuse):
        return join(self.pattern_classes_base_path, misuse.misuse_id)

    def get_dependency_classpath(self):
        if isdir(self.dependencies_path):
            return ":".join([join(self.dependencies_path, file) for file in os.listdir(self.dependencies_path) if file.endswith(".jar")])
        else:
            return ""
