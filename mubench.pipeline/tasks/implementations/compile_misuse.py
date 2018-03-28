import logging
import os
import shutil
from glob import glob
from os import makedirs
from os.path import join, dirname, splitext, relpath, exists

from data.misuse import Misuse
from data.version_compile import VersionCompile
from utils.io import copy_tree
from utils.shell import Shell


class CompileMisuseTask:
    def __init__(self, compile_base_path: str, run_timestamp: int, force_compile: bool):
        self.compile_base_path = compile_base_path
        self.run_timestamp = run_timestamp
        self.force_compile = force_compile

    def run(self, misuse: Misuse, version_compile: VersionCompile):
        logger = logging.getLogger("task.compile_patterns")

        misuse_compile = misuse.get_misuse_compile(self.compile_base_path)

        if self.force_compile or version_compile.timestamp > misuse_compile.timestamp:
            misuse_compile.delete()

        logger.info("Compiling %s...", misuse)

        if not exists(misuse_compile.misuse_source_path):
            logger.debug("Copying misuse sources...")
            for source_path in version_compile.original_sources_paths:
                CompileMisuseTask._copy_misuse_sources(source_path, misuse, misuse_compile.misuse_source_path)

        if not exists(misuse_compile.misuse_classes_path):
            logger.debug("Copying misuse classes...")
            for classes_path in version_compile.original_classes_paths:
                CompileMisuseTask._copy_misuse_classes(classes_path, misuse, misuse_compile.misuse_classes_path)

        try:
            if misuse_compile.needs_copy_sources() or misuse_compile.needs_compile():
                logger.info("Compiling correct usage for %s...", misuse)

            if misuse_compile.needs_copy_sources():
                logger.debug("Copying correct-usage sources...")
                copy_tree(misuse.correct_usage_path, misuse_compile.correct_usage_sources_path)

            if misuse_compile.needs_compile():
                logger.debug("Compiling correct usages...")
                CompileMisuseTask._compile_correct_usages(misuse_compile.correct_usage_sources_path,
                                                    misuse_compile.correct_usage_classes_path,
                                                    version_compile.get_full_classpath())
                misuse_compile.save(self.run_timestamp)
            elif misuse.correct_usages:
                logger.info("Correct usage already compiled.")
        except Exception:
            misuse_compile.delete()
            raise

        return misuse_compile

    @staticmethod
    def _compile_correct_usages(source: str, destination: str, classpath: str):
        makedirs(destination, exist_ok=True)
        for root, dirs, files in os.walk(source):
            for java_file in [f for f in files if f.endswith(".java")]:
                destination = dirname(join(destination, java_file))
                Shell.exec('javac "{}" -d "{}" -cp "{}"'.format(join(root, java_file), destination, classpath),
                           logger=logging.getLogger("task.compile_correct_usages.compile"))

    @staticmethod
    def _copy_misuse_sources(sources_path, misuse, destination):
        file = misuse.location.file
        if exists(join(sources_path, file)):
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
