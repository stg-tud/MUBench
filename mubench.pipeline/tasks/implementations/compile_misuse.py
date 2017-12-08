import logging
from glob import glob
from os import makedirs
from os.path import join, basename, dirname, splitext, relpath
from shutil import move
from typing import Set

import shutil

from data.misuse import Misuse
from data.pattern import Pattern
from data.version_compile import VersionCompile
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

        logger.debug("Copy misuse sources...")
        CompileMisuseTask._copy_misuse_sources(version_compile.original_sources_path,
                                               misuse,
                                               pattern_compile.misuse_source_path)
        logger.debug("Copy misuse classes...")
        CompileMisuseTask._copy_misuse_classes(version_compile.original_classes_path,
                                               misuse,
                                               pattern_compile.misuse_classes_path)

        try:
            if pattern_compile.needs_copy_sources():
                logger.info("Copying patterns...")
                CompileMisuseTask._copy_patterns(misuse.patterns, pattern_compile.get_source_path())

            if pattern_compile.needs_compile():
                logger.info("Compiling patterns...")

                source_files = set()
                for pattern in pattern_compile.patterns:
                    source_files.add(pattern.path)

                CompileMisuseTask._compile(source_files,
                                           pattern_compile.get_classes_path(),
                                           version_compile.get_full_classpath())
            else:
                logger.info("Patterns already compiled.")
        except Exception:
            pattern_compile.delete()
            raise

        return pattern_compile

    @staticmethod
    def _compile(source_files: Set[str], destination: str, classpath: str):
        logger = logging.getLogger("task.compile_patterns.compile")
        Shell.exec('javac -cp "{}" "{}"'.format(classpath, '" "'.join(source_files)), logger=logger)
        logger.debug('Copying class files to "{}"'.format(destination))
        makedirs(destination, exist_ok=True)
        for source_file in source_files:
            class_file = source_file.split('.')[0] + '.class'
            logger.debug('Copying class file "{}"...'.format(class_file))
            move(class_file, join(destination, basename(class_file)))

    @staticmethod
    def _copy_patterns(patterns: Set[Pattern], destination: str):
        for pattern in patterns:
            pattern.copy(destination)

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
