import os
from os.path import join, exists, relpath, basename
from tempfile import mkdtemp
from unittest.mock import patch, MagicMock, PropertyMock

from data.pattern import Pattern
from tasks.implementations.compile_misuse import CompileMisuseTask
from tests.test_utils.data_util import create_misuse, create_project, create_version
from utils.io import remove_tree, create_file


class TestCompilePatterns:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-patterns-test_")
        self.data_base_path = join(self.temp_dir, "data")
        self.compile_base_path = join(self.temp_dir, "-compile-")

        self.project = create_project("-project-", base_path=self.data_base_path)
        self.version = create_version("-version-", project=self.project)
        self.pattern = Pattern(join(self.data_base_path, "-project-", "misuses", "-misuse-", "patterns"),
                               join("-package-", "-pattern-.java"))
        create_file(self.pattern.path)
        self.misuse = create_misuse("-misuse-", project=self.project, version=self.version,
                                    patterns=[self.pattern], meta={})
        self.version._YAML = {"build": {"src": "src/java", "classes": "target/classes"}}

        self.compile = self.version.get_compile(self.compile_base_path)
        self.compile.get_full_classpath = lambda: join(self.temp_dir, "dependencies.jar")

        create_file(join(self.compile.original_sources_paths[0], self.misuse.location.file))

        self.misuse_compile = self.misuse.get_misuse_compile(self.compile_base_path)
        self.misuse.get_misuse_compile = lambda *_: self.misuse_compile

        self.compile_patch = patch('tasks.implementations.compile_misuse.CompileMisuseTask._compile_patterns')
        self.compile_mock = self.compile_patch.start()

        def create_classes(source, destination, _):
            for root, dirs, files in os.walk(source):
                package = relpath(root, source)
                for file in files:
                    file = file.replace(".java", ".class")
                    create_file(join(destination, package, file))
                    print("fake compile: {}".format(join(destination, package, file)))

        self.compile_mock.side_effect = create_classes

    def teardown(self):
        remove_tree(self.temp_dir)
        self.compile_patch.stop()

    def test_copies_pattern_sources(self):
        uut = CompileMisuseTask(self.compile_base_path, 0, force_compile=False)

        uut.run(self.misuse, self.compile)

        assert exists(self.misuse_compile.pattern_sources_path)

    def test_compiles_patterns(self):
        uut = CompileMisuseTask(self.compile_base_path, 0, force_compile=False)

        uut.run(self.misuse, self.compile)

        self.compile_mock.assert_called_once_with(self.misuse_compile.pattern_sources_path,
                                                  self.misuse_compile.pattern_classes_path,
                                                  self.compile.get_full_classpath())

    def test_skips_compile_if_not_needed(self):
        uut = CompileMisuseTask(self.compile_base_path, 0, force_compile=False)
        self.misuse_compile.needs_compile = lambda: False

        uut.run(self.misuse, self.compile)

        self.compile_mock.assert_not_called()

    def test_forces_compile_patterns(self):
        uut = CompileMisuseTask(self.compile_base_path, 0, force_compile=True)
        self.misuse_compile.delete = MagicMock()
        self.misuse_compile.needs_compile = lambda: self.misuse_compile.delete.calls

        uut.run(self.misuse, self.compile)

        self.compile_mock.assert_called_once_with(self.misuse_compile.pattern_sources_path,
                                                  self.misuse_compile.pattern_classes_path,
                                                  self.compile.get_full_classpath())

    def test_copies_misuse_sources(self):
        uut = CompileMisuseTask(self.compile_base_path, 0, force_compile=False)

        create_file(join(self.compile.original_sources_paths[0], "mu.file"))
        misuse = create_misuse("1", meta={"location": {"file": "mu.file"}}, project=self.project, version=self.version)

        pattern_compile = uut.run(misuse, self.compile)

        assert exists(join(pattern_compile.misuse_source_path, "mu.file"))

    def test_copies_misuse_classes(self):
        uut = CompileMisuseTask(self.compile_base_path, 0, force_compile=False)

        create_file(join(self.compile.original_sources_paths[0], "mu.java"))
        create_file(join(self.compile.original_classes_paths[0], "mu.class"))
        misuse = create_misuse("1", meta={"location": {"file": "mu.java"}}, project=self.project, version=self.version)

        pattern_compile = uut.run(misuse, self.compile)

        assert exists(join(pattern_compile.misuse_classes_path, "mu.class"))

    def test_copies_misuse_inner_classes(self):
        uut = CompileMisuseTask(self.compile_base_path, 0, force_compile=False)

        misuse = create_misuse("1", meta={"location": {"file": "mu.java"}}, project=self.project, version=self.version)
        create_file(join(self.compile.original_sources_paths[0], "mu.java"))
        create_file(join(self.compile.original_classes_paths[0], "mu.class"))
        create_file(join(self.compile.original_classes_paths[0], "mu$1.class"))
        create_file(join(self.compile.original_classes_paths[0], "mu$Inner.class"))

        pattern_compile = uut.run(misuse, self.compile)

        assert exists(join(pattern_compile.misuse_classes_path, "mu.class"))
        assert exists(join(pattern_compile.misuse_classes_path, "mu$1.class"))
        assert exists(join(pattern_compile.misuse_classes_path, "mu$Inner.class"))

    @patch("data.version_compile.VersionCompile.timestamp", new_callable=PropertyMock)
    @patch("data.misuse_compile.MisuseCompile.timestamp", new_callable=PropertyMock)
    def test_force_compile_if_version_compile_is_more_recent(self, misuse_compile_timestamp_mock,
                                                             version_compile_timestamp_mock):
        uut = CompileMisuseTask(self.compile_base_path, 0, force_compile=False)
        uut.force_compile = False
        self.misuse_compile.delete = MagicMock()
        self.misuse_compile.needs_compile = lambda: self.misuse_compile.delete.calls
        misuse_compile_timestamp_mock.return_value = 1
        version_compile_timestamp_mock.return_value = 2

        uut.run(self.misuse, self.compile)

        self.compile_mock.assert_called_once_with(self.misuse_compile.pattern_sources_path,
                                                  self.misuse_compile.pattern_classes_path,
                                                  self.compile.get_full_classpath())
