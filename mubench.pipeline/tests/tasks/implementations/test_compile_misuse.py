from os.path import join, exists
from tempfile import mkdtemp
from unittest.mock import patch, MagicMock

from data.pattern import Pattern
from tasks.implementations.compile_misuse import CompileMisuseTask
from tests.test_utils.data_util import create_misuse, create_project, create_version
from utils.io import remove_tree, create_file


@patch('tasks.implementations.compile_misuse.CompileMisuseTask._copy_misuse_sources')
@patch('tasks.implementations.compile_misuse.CompileMisuseTask._copy_misuse_classes')
@patch('tasks.implementations.compile_misuse.CompileMisuseTask._copy_patterns')
@patch('tasks.implementations.compile_misuse.CompileMisuseTask._compile')
class TestCompilePatterns:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-patterns-test_")
        self.data_base_path = join(self.temp_dir, "data")
        self.compile_base_path = join(self.temp_dir, "-compile-")

        project = create_project("-project-", base_path=self.data_base_path)
        self.pattern = Pattern(join(self.data_base_path, "-project-", "-misuse-", "patterns"),
                               join("-package-", "-pattern-.java"))
        self.misuse = create_misuse("-misuse-", project=project,
                                    patterns=[self.pattern])
        version = create_version("-version-", project=project, misuses=[self.misuse])

        self.compile = version.get_compile(self.compile_base_path)
        self.compile.get_full_classpath = lambda: join(self.temp_dir, "dependencies.jar")

        self.misuse_compile = self.misuse.get_misuse_compile(self.compile_base_path)
        self.misuse.get_misuse_compile = lambda *_: self.misuse_compile

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_copies_pattern_sources(self, _, copy_patterns_mock, __, ___):
        uut = CompileMisuseTask(self.compile_base_path, force_compile=False)

        uut.run(self.misuse, self.compile)

        copy_patterns_mock.assert_called_once_with(self.misuse.patterns, self.misuse_compile.get_source_path())

    def test_compiles_patterns(self, compile_mock, _, __, ___):
        uut = CompileMisuseTask(self.compile_base_path, force_compile=False)

        uut.run(self.misuse, self.compile)

        compile_mock.assert_called_once_with({self.pattern.path},
                                             self.misuse_compile.get_classes_path(),
                                             self.compile.get_full_classpath())

    def test_skips_compile_if_not_needed(self, compile_mock, _, __, ___):
        uut = CompileMisuseTask(self.compile_base_path, force_compile=False)
        self.misuse_compile.needs_compile = lambda: False

        uut.run(self.misuse, self.compile)

        compile_mock.assert_not_called()

    def test_forces_compile_patterns(self, compile_mock, _, __, ___):
        uut = CompileMisuseTask(self.compile_base_path, force_compile=True)
        self.misuse_compile.delete = MagicMock()

        uut.run(self.misuse, self.compile)

        self.misuse_compile.delete.assert_called_once_with()
        compile_mock.assert_called_once_with({self.pattern.path},
                                             self.misuse_compile.get_classes_path(),
                                             self.compile.get_full_classpath())


class TestCopyMisuseFiles:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-patterns-test_")
        self.data_base_path = join(self.temp_dir, "data")
        self.compile_base_path = join(self.temp_dir, "-compile-")

        self.project = create_project("-project-", base_path=self.data_base_path)
        self.version = create_version("-version-", project=self.project)

        self.compile = self.version.get_compile(self.compile_base_path)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_copies_misuse_sources(self):
        uut = CompileMisuseTask(self.compile_base_path, force_compile=False)

        create_file(join(self.compile.original_sources_path, "mu.file"))
        misuse = create_misuse("1", meta={"location": {"file": "mu.file"}}, project=self.project, version=self.version)

        pattern_compile = uut.run(misuse, self.compile)

        assert exists(join(pattern_compile.misuse_source_path, "mu.file"))

    def test_copies_misuse_classes(self):
        uut = CompileMisuseTask(self.compile_base_path, force_compile=False)

        create_file(join(self.compile.original_sources_path, "mu.java"))
        create_file(join(self.compile.original_classes_path, "mu.class"))
        misuse = create_misuse("1", meta={"location": {"file": "mu.java"}}, project=self.project, version=self.version)

        pattern_compile = uut.run(misuse, self.compile)

        assert exists(join(pattern_compile.misuse_classes_path, "mu.class"))

    def test_copies_misuse_inner_classes(self):
        uut = CompileMisuseTask(self.compile_base_path, force_compile=False)

        misuse = create_misuse("1", meta={"location": {"file": "mu.java"}}, project=self.project, version=self.version)
        create_file(join(self.compile.original_sources_path, "mu.java"))
        create_file(join(self.compile.original_classes_path, "mu.class"))
        create_file(join(self.compile.original_classes_path, "mu$1.class"))
        create_file(join(self.compile.original_classes_path, "mu$Inner.class"))

        pattern_compile = uut.run(misuse, self.compile)

        assert exists(join(pattern_compile.misuse_classes_path, "mu.class"))
        assert exists(join(pattern_compile.misuse_classes_path, "mu$1.class"))
        assert exists(join(pattern_compile.misuse_classes_path, "mu$Inner.class"))
