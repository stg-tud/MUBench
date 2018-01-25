import os
from logging import Logger
from os import makedirs
from os.path import join, exists, dirname, relpath
from shutil import rmtree
from tempfile import mkdtemp
from typing import List
from unittest.mock import MagicMock, ANY, patch, PropertyMock

from nose.tools import assert_raises, assert_equals

from tasks.implementations.compile_version import CompileVersionTask
from tests.test_utils.data_util import create_version, create_project
from utils.io import create_file
from utils.shell import CommandFailedError


class TestCompileVersion:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-test_")
        self.project_path = join(self.temp_dir, "project")
        self.version_path = join(self.project_path, "versions", "v0")
        self.checkout_base_path = join(self.temp_dir, "checkouts")
        self.compile_base_path = self.checkout_base_path

        self.source_dir = "src"
        self.project = create_project(self.project_path, meta={"repository": {"type": "git", "url": "-url-"}})
        self.version = create_version(self.version_path, project=self.project,
                                      meta={"build": {"src": self.source_dir,
                                                      "commands": ["mkdir classes"],
                                                      "classes": "classes"},
                                            "revision": "0"},
                                      misuses=[])

        self.checkout = self.version.get_checkout(self.checkout_base_path)

        self.checkout_path = self.checkout.checkout_dir
        self.source_path = join(self.checkout_path, self.source_dir)
        makedirs(self.source_path)

        self.base_path = dirname(self.checkout_path)
        self.build_path = join(self.base_path, "build")
        self.dep_path = join(self.base_path, "dependencies")

        self.run_timestamp = 1516186439
        self.uut = CompileVersionTask(self.compile_base_path, self.run_timestamp, False, False)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def mock_with_fake_compile(self):
        def mock_compile(commands: List[str], cwd: str, dep_dir: str,
                         compile_base_path: str, logger: Logger):
            source_path = join(cwd, self.source_dir)
            class_path = join(cwd, "classes")
            makedirs(class_path, exist_ok=True)
            for root, dirs, files in os.walk(source_path):
                package = relpath(root, source_path)
                for file in files:
                    file = file.replace(".java", ".class")
                    create_file(join(class_path, package, file))
                    print("fake compile: {}".format(join(class_path, package, file)))

        self.uut._compile = MagicMock(side_effect=mock_compile)

    def test_skips_if_no_config(self):
        self.mock_with_fake_compile()
        del self.version._YAML["build"]

        assert_raises(UserWarning, self.uut.run, self.version, self.checkout)

    def test_passes_compile_commands(self):
        self.mock_with_fake_compile()
        self.version._YAML["build"]["commands"] = ["a", "b"]

        self.uut.run(self.version, self.checkout)

        self.uut._compile.assert_called_with(["a", "b"],
                                             self.build_path,
                                             self.dep_path,
                                             self.compile_base_path,
                                             ANY)

    def test_copies_additional_sources(self):
        self.mock_with_fake_compile()
        create_file(join(self.version_path, "compile", "additional.file"))

        self.uut.run(self.version, self.checkout)

        assert exists(join(self.build_path, "additional.file"))

    def test_skips_on_build_error(self):
        self.mock_with_fake_compile()
        self.uut._compile.side_effect = CommandFailedError("-cmd-", "-error message-")

        assert_raises(CommandFailedError, self.uut.run, self.version, self.checkout)

    def test_saves_compile_timestamp(self):
        self.mock_with_fake_compile()

        self.uut.run(self.version, self.checkout)

        assert_equals(self.run_timestamp, self.version.get_compile(self.base_path).timestamp)

    def test_skips_compile_if_saved_compile_exists(self):
        self.mock_with_fake_compile()
        self.version.get_compile(self.project_path).save(self.run_timestamp)

        self.uut.run(self.version, self.checkout)

        self.uut._compile.assert_not_called()

    def test_forces_compile(self):
        self.mock_with_fake_compile()
        self.version.get_compile(self.project_path).save(self.run_timestamp)
        self.uut.force_compile = True

        self.uut.run(self.version, self.checkout)

        assert self.uut._compile.call_args_list, "not called"

    @patch("data.project_checkout.ProjectCheckout.timestamp", new_callable=PropertyMock)
    @patch("data.version_compile.VersionCompile.timestamp", new_callable=PropertyMock)
    def test_forces_compile_if_checkout_is_more_recent(self, compile_timestamp_mock, checkout_timestamp_mock):
        self.version.get_compile(self.project_path).save(self.run_timestamp)
        self.mock_with_fake_compile()
        self.uut.force_compile = False
        compile_timestamp_mock.return_value = 1
        checkout_timestamp_mock.return_value = 2

        self.uut.run(self.version, self.checkout)

        assert self.uut._compile.call_args_list, "not called"
