from os.path import join, isdir


class ProjectCompile:
    ORIGINAL_SOURCE_DIR = "original-src"
    ORIGINAL_CLASSES_DIR = "original-classes"
    MISUSE_SOURCE_DIR = "misuse-src"
    MISUSE_CLASSES_DIR = "misuse-classes"
    PATTERN_SOURCE_DIR = "patterns-src"
    PATTERN_CLASSES_DIR = "patterns-classes"

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.original_sources_path = join(self.base_path, ProjectCompile.ORIGINAL_SOURCE_DIR)
        self.original_classes_path = join(self.base_path, ProjectCompile.ORIGINAL_CLASSES_DIR)
        self.misuse_source_path = join(self.base_path, ProjectCompile.MISUSE_SOURCE_DIR)
        self.misuse_classes_path = join(self.base_path, ProjectCompile.MISUSE_CLASSES_DIR)
        self.pattern_sources_path = join(self.base_path, ProjectCompile.PATTERN_SOURCE_DIR)
        self.pattern_classes_path = join(self.base_path, ProjectCompile.PATTERN_CLASSES_DIR)

    def needs_copy_sources(self):
        return not isdir(self.original_sources_path)

    def needs_copy_pattern_sources(self):
        return not isdir(self.pattern_sources_path)

    def needs_compile(self):
        return not isdir(self.original_classes_path)

    def needs_compile_patterns(self):
        return not isdir(self.pattern_classes_path)
