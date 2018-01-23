import logging
import shutil
from glob import glob
from os import makedirs, walk
from os.path import join, dirname, splitext, relpath
from typing import List

from data.misuse import Misuse
from data.version_compile import VersionCompile
from utils.io import copy_tree
from utils.shell import Shell


class CompileMisuseTask:
    def __init__(self, compile_base_path: str, force_compile: bool):
        self.compile_base_path = compile_base_path
        self.force_compile = force_compile

    def run(self, misuse: Misuse, version_compile: VersionCompile):
        logger = logging.getLogger("task.compile_patterns")

        pattern_compile = misuse.get_misuse_compile(self.compile_base_path)

        if self.force_compile:
            pattern_compile.delete()

        logger.info("Compiling %s...", misuse)

        logger.debug("Copying misuse sources...")
        CompileMisuseTask._copy_misuse_sources(version_compile.original_sources_path,
                                               misuse,
                                               pattern_compile.misuse_source_path)
        logger.debug("Copying misuse classes...")
        CompileMisuseTask._copy_misuse_classes(version_compile.original_classes_path,
                                               misuse,
                                               pattern_compile.misuse_classes_path)

        try:
            logger.info("Compiling correct usage for %s...", misuse)
            if pattern_compile.needs_copy_sources():
                logger.debug("Copying correct-usage sources...")
                copy_tree(misuse.pattern_path, pattern_compile.pattern_sources_path)

            if pattern_compile.needs_compile():
                logger.debug("Compiling correct usages...")
                CompileMisuseTask._compile_patterns(pattern_compile.pattern_sources_path,
                                                    pattern_compile.pattern_classes_path,
                                                    version_compile.get_full_classpath())
            else:
                logger.info("Correct usage already compiled.")
        except Exception:
            pattern_compile.delete()
            raise

        return pattern_compile

    @staticmethod
    def _compile_patterns(source: str, destination: str, classpath: str):
        makedirs(destination, exist_ok=True)
        for root, dirs, files in walk(source):
            for java_file in [f for f in files if f.endswith(".java")]:
                destination = dirname(join(destination, java_file))
                Shell.exec('javac "{}" -d "{}" -cp "{}"'.format(join(root, java_file), destination, classpath),
                           logger=logging.getLogger("task.compile_patterns.compile"))

    @staticmethod
    def _copy_misuse_sources(sources_path, misuse, destination):
        file = misuse.location.file
        dst = join(destination, file)
        makedirs(dirname(dst), exist_ok=True)
        shutil.copy(join(sources_path, file), dst)

    @staticmethod
    def _copy_misuse_classes(classes_path, misuse, destination):
        basepath = join(classes_path, splitext(misuse.location.file)[0])
        classes = glob(basepath + ".class") + glob(basepath + "$*.class")
        for class_ in classes:
            dst = join(destination, relpath(class_, classes_path))
            makedirs(dirname(dst), exist_ok=True)
            shutil.copy(class_, dst)
