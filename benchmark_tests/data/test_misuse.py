from os import makedirs
from os.path import join, dirname, exists
from shutil import rmtree
from tempfile import mkdtemp

import yaml
from benchmark.data.misuse import Misuse, BuildConfig
from nose.tools import assert_equals, assert_not_equals, assert_raises
from typing import Dict, Union, Set

from benchmark.data.pattern import Pattern
from benchmark.data.project_checkout import LocalProjectCheckout, GitProjectCheckout, SVNProjectCheckout
from benchmark.utils.io import safe_write
from benchmark.utils.shell import Shell


class TMisuse(Misuse):
    def __init__(self, path: str = ":irrelevant:", meta: Dict[str, Union[str, Dict]]={}):
        Misuse.__init__(self, path)
        self._META = meta


# noinspection PyAttributeOutsideInit
class TestMisuse:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-misuse.')

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_extracts_name(self):
        uut = Misuse("/MUBench/data/project.id")
        assert uut.name == "project.id"

    def test_finds_meta_file(self):
        uut = Misuse("MUBench/data/project.id")
        assert_equals(uut.meta_file, join("MUBench/data/project.id", "meta.yml"))

    def test_extracts_project_name(self):
        uut = Misuse(join("C:", "my-path", "project.42-2"))
        assert_equals("project", uut.project_name)

    def test_extracts_synthetic_project_name(self):
        uut = Misuse((join("C:", "my-path", "synthetic-example")))
        assert_equals("synthetic-example", uut.project_name)

    def test_extracts_version(self):
        uut = Misuse("project.version")
        assert_equals("version", uut.project_version)

    def test_extracts_version_from_synthetic(self):
        uut = Misuse("synthetic")
        assert_equals(None, uut.project_version)

    def test_reads_meta_file(self):
        uut = Misuse(self.temp_dir)

        safe_write(yaml.dump({'key': 'value'}), uut.meta_file, append=False)

        assert uut.meta['key'] == 'value'

    def test_finds_no_pattern(self):
        uut = Misuse(self.temp_dir)

        assert uut.patterns == set()

    def test_finds_single_pattern(self):
        uut = Misuse(self.temp_dir)

        expected = self.create_pattern_file(uut, "APattern.java")

        assert_equals(uut.patterns, {expected})

    def test_finds_multiple_patterns(self):
        uut = Misuse(self.temp_dir)

        pattern1 = self.create_pattern_file(uut, "OnePattern.java")
        pattern2 = self.create_pattern_file(uut, "AnotherPattern.java")

        assert_equals(uut.patterns, {pattern1, pattern2})

    def test_finds_pattern_in_package(self):
        uut = Misuse(self.temp_dir)

        pattern = self.create_pattern_file(uut, join("mypackage", "Pattern.java"))

        assert_equals(uut.patterns, {pattern})

    def test_equals_by_path(self):
        assert Misuse("foo/bar") == Misuse("foo/bar")

    def test_differs_by_path(self):
        assert Misuse("foo/bar") != Misuse("bar/bazz")

    def test_extracts_build_config(self):
        uut = TMisuse("/path/misuse",
                      {"build": {"src": "src/java/", "commands": ["mvn compile"], "classes": "target/classes/"}})

        actual_config = uut.build_config
        assert_equals("src/java/", actual_config.src)
        assert_equals(["mvn compile"], actual_config.commands)
        assert_equals("target/classes/", actual_config.classes)

    def test_build_config_is_none_if_any_part_is_missing(self):
        uut = TMisuse("/path/misuse", {"build": {"src": "src/java/", "classes": "target/classes/"}})
        assert uut.build_config is None

    def test_derives_additional_compile_sources_path(self):
        uut = TMisuse("/path/misuse")
        assert_equals(join("/path/misuse", "compile"), uut.additional_compile_sources)

    @staticmethod
    def create_pattern_file(misuse: Misuse, filename: str) -> Pattern:
        patterns_path = join(misuse.path, "patterns")
        path = join(patterns_path, filename)
        directory = dirname(path)
        if not exists(directory):
            makedirs(directory)
        open(path, 'a').close()
        return Pattern(patterns_path, filename)


class TestBuildConfig:
    def test_to_string(self):
        assert_equals("[src: a, classes: b, commands: ['echo c', 'echo d']]",
                      str(BuildConfig("a", ["echo c", "echo d"], "b")))

    def test_equals(self):
        assert BuildConfig("src", ["command"], "classes") == BuildConfig("src", ["command"], "classes")

    def test_not_equals_src(self):
        assert BuildConfig("src", ["command"], "classes") != BuildConfig("other", ["command"], "classes")

    def test_not_equals_command(self):
        assert BuildConfig("src", ["command"], "classes") != BuildConfig("src", ["other"], "classes")

    def test_not_equals_classes(self):
        assert BuildConfig("src", ["command"], "classes") != BuildConfig("src", ["command"], "other")

    def test_hash_not_equals(self):
        assert_not_equals(hash(BuildConfig("", [], "")), hash(BuildConfig("a", ["b"], "c")))

    def test_hash_equals(self):
        assert_equals(hash(BuildConfig("a", ["b"], "c")), hash(BuildConfig("a", ["b"], "c")))


class TestProjectCheckout:
    def test_synthetic_project(self):
        uut = TMisuse(":project:", meta={"fix": {"repository": {"type": "synthetic"}}})

        checkout = uut.get_checkout(None, ":base_path:")

        assert isinstance(checkout, LocalProjectCheckout)
        assert_equals(join(":project:", "compile"), checkout.url)
        assert_equals(":project:", checkout.name)

    def test_git_project(self):
        uut = TMisuse(":project:.:version:", meta={"fix":
                                                       {"repository": {"type": "git", "url": "ssh://foobar.git"},
                                                        "revision": ":revision:"}})

        checkout = uut.get_checkout(None, ":base_path:")

        assert isinstance(checkout, GitProjectCheckout)
        assert_equals("ssh://foobar.git", checkout.url)
        assert_equals(":project:", checkout.name)
        assert_equals(":version:", checkout.version)
        assert_equals(":revision:~1", checkout.revision)

    def test_svn_project(self):
        uut = TMisuse(":project:.:version:", meta={"fix":
                                                       {"repository": {"type": "svn", "url": "http://url/svn"},
                                                        "revision": "667"}})

        checkout = uut.get_checkout(None, ":base_path:")

        assert isinstance(checkout, SVNProjectCheckout)
        assert_equals("http://url/svn", checkout.url)
        assert_equals(":project:", checkout.name)
        assert_equals(":version:", checkout.version)
        assert_equals("666", checkout.revision)

    def test_unknown_type(self):
        with assert_raises(ValueError):
            uut = TMisuse("", meta={"fix": {"repository": {"type": ":unknown type:"}}})
            uut.get_checkout(None, ":irrelevant:")

