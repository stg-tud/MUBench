import os
from os.path import join, isdir, exists
from typing import List

from data.misuse import Misuse
from utils.io import remove_tree, write_yaml, read_yaml


class VersionCompile:
    ORIGINAL_SOURCE_DIR = "original-src"
    ORIGINAL_CLASSES_DIR = "original-classes"
    MISUSE_SOURCE_DIR = "misuse-src"
    MISUSE_CLASSES_DIR = "misuse-classes"
    DEPENDENCY_DIR = "dependencies"
    __BUILD_DIR = "build"
    __COMPILE_INFO_FILE = "compile.yml"
    __KEY_TIMESTAMP = "timestamp"
    __DEFAULT_TIMESTAMP = 0

    def __init__(self, base_path: str, misuses: List[Misuse]):
        self.base_path = base_path
        self.misuses = misuses

        self.original_sources_path = join(self.base_path, VersionCompile.ORIGINAL_SOURCE_DIR)
        self.original_classes_path = join(self.base_path, VersionCompile.ORIGINAL_CLASSES_DIR)
        self.original_classpath = self.original_classes_path + ".jar"
        self.dependencies_path = join(self.base_path, VersionCompile.DEPENDENCY_DIR)
        self.build_dir = join(self.base_path, VersionCompile.__BUILD_DIR)
        self._compile_info_file = join(self.build_dir, self.__COMPILE_INFO_FILE)

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

    @property
    def timestamp(self) -> int:
        timestamp = VersionCompile.__DEFAULT_TIMESTAMP

        if exists(self._compile_info_file):
            checkout_info = read_yaml(self._compile_info_file)
            timestamp = checkout_info.get(VersionCompile.__KEY_TIMESTAMP, VersionCompile.__DEFAULT_TIMESTAMP)

        return timestamp

    def save(self, current_timestamp: int):
        compile_info = {VersionCompile.__KEY_TIMESTAMP: current_timestamp}
        write_yaml(compile_info, self._compile_info_file)

    def delete(self):
        remove_tree(self.original_sources_path)
        remove_tree(self.original_classes_path)
        remove_tree(self.build_dir)
