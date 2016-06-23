from os.path import join


class ProjectCompile:
    ORIGINAL_SOURCE_DIR = "original-src"
    ORIGINAL_CLASSES_DIR = "original-classes"
    PATTERN_SOURCE_DIR = "patterns-src"
    PATTERN_CLASSES_DIR = "patterns-classes"

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.original_sources_path = join(self.base_path, ProjectCompile.ORIGINAL_SOURCE_DIR)
        self.original_classes_path = join(self.base_path, ProjectCompile.ORIGINAL_CLASSES_DIR)
        self.pattern_sources_path = join(self.base_path, ProjectCompile.PATTERN_SOURCE_DIR)
        self.pattern_classes_path = join(self.base_path, ProjectCompile.PATTERN_CLASSES_DIR)
