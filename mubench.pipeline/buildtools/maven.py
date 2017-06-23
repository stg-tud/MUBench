import os


class Project:
    def __init__(self, base_path):
        self.base_path = base_path

    def get_sources_paths(self):
        source_paths = {}
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(".java"):
                    source_root = self.__get_source_root(file, root)
                    if source_root:
                        source_root = os.path.relpath(source_root, self.base_path)
                        if "test" not in source_root:
                            source_paths[source_root] = 1
        return list(source_paths.keys())

    def __get_source_root(self, file, root):
        source_path = root
        for package_name in reversed(self.__get_package_names(os.path.join(root, file))):
            if os.path.basename(source_path) == package_name:
                source_path = os.path.dirname(source_path)
            else:
                source_path = None
                break
        return source_path

    @staticmethod
    def __get_package_names(java_file_path):
        try:
            with open(java_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                try:
                    package_declaration = next(line for line in f.readlines() if "package " in line)  # type: str
                    package_name_start = package_declaration.find("package ") + 8
                    package_name_end = package_declaration.find(";", package_name_start)
                    return package_declaration[package_name_start:package_name_end].split(".")
                except StopIteration:
                    return []
        except FileNotFoundError:
            return []  # somehow this seems to happen for empty files
