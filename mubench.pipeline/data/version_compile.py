import os
from os.path import join, isdir, exists

from utils.io import remove_tree, write_yaml, read_yaml


class VersionCompile:
    DEPENDENCY_DIR = "dependencies"
    __BUILD_DIR = "build"
    __COMPILE_INFO_FILE = "compile.yml"
    __KEY_TIMESTAMP = "timestamp"
    __DEFAULT_TIMESTAMP = 0

    def __init__(self, base_path: str, relative_sources_paths: str, relative_classes_path: str):
        self.build_dir = join(base_path, VersionCompile.__BUILD_DIR)
        self.original_sources_paths = [join(self.build_dir, rel_path.lstrip(os.path.sep))
                                       for rel_path in relative_sources_paths]
        self.original_classes_paths = [join(self.build_dir, rel_path.lstrip(os.path.sep))
                                       for rel_path in relative_classes_path]
        self.original_classpath = join(base_path, "original-classes.jar")
        self.dependencies_path = join(base_path, VersionCompile.DEPENDENCY_DIR)
        self._compile_info_file = join(self.build_dir, self.__COMPILE_INFO_FILE)

    def needs_compile(self):
        return not exists(self._compile_info_file)

    def get_dependency_classpath(self):
        if isdir(self.dependencies_path):
            return ":".join([join(self.dependencies_path, file)
                             for file in os.listdir(self.dependencies_path) if file.endswith(".jar")])
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
        remove_tree(self.build_dir)
