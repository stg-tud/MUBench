import os
from os.path import join, isdir
from typing import List

from data.misuse import Misuse
from utils.io import remove_tree


class VersionCompile:
    ORIGINAL_SOURCE_DIR = "original-src"
    ORIGINAL_CLASSES_DIR = "original-classes"
    MISUSE_SOURCE_DIR = "misuse-src"
    MISUSE_CLASSES_DIR = "misuse-classes"
    DEPENDENCY_DIR = "dependencies"
    __BUILD_DIR = "build"

    def __init__(self, base_path: str, misuses: List[Misuse]):
        self.base_path = base_path
        self.misuses = misuses

        self.original_sources_path = join(self.base_path, VersionCompile.ORIGINAL_SOURCE_DIR)
        self.original_classes_path = join(self.base_path, VersionCompile.ORIGINAL_CLASSES_DIR)
        self.original_classpath = self.original_classes_path + ".jar"
        self.dependencies_path = join(self.base_path, VersionCompile.DEPENDENCY_DIR)
        self.build_dir = join(self.base_path, VersionCompile.__BUILD_DIR)

    def needs_copy_sources(self):
        return not isdir(self.original_classes_path)

    def needs_compile(self):
        return not isdir(self.original_classes_path)

    def get_dependency_classpath(self):
        if isdir(self.dependencies_path):
            return ":".join([join(self.dependencies_path, file) for file in os.listdir(self.dependencies_path) if file.endswith(".jar")])
        else:
            return ""

    def get_full_classpath(self):
        dependency_classpath = self.get_dependency_classpath()
        if dependency_classpath:
            return "{}:{}".format(dependency_classpath, self.original_classpath)
        else:
            return self.original_classpath

    def delete(self):
        remove_tree(self.original_sources_path)
        remove_tree(self.original_classes_path)
        remove_tree(self.build_dir)
