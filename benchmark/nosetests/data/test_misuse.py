from os import makedirs
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

import yaml
from benchmark.data.misuse import Misuse, BuildConfig
from nose.tools import assert_equals, assert_not_equals
from typing import Dict, Union

from benchmark.data.pattern import Pattern
from benchmark.utils.io import safe_write


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
        assert "project" == uut.project_name

    def test_extracts_synthetic_project_name(self):
        uut = Misuse((join("C:", "my-path", "synthetic-example")))
        assert "synthetic-example" == uut.project_name

    def test_reads_meta_file(self):
        uut = Misuse(self.temp_dir)

        safe_write(yaml.dump({'key': 'value'}), uut.meta_file, append=False)

        assert uut.meta['key'] == 'value'

    def test_repository(self):
        uut = TMisuse(meta={"fix": {"repository": {"type": "git", "url": "ssh://foobar.git"}}})
        repo = uut.repository

        assert_equals("git", repo.type)
        assert_equals("ssh://foobar.git", repo.url)

    def test_synthetic_repository(self):
        uut = TMisuse("/path/misuse", {"fix": {"repository": {"type": "synthetic"}}})
        repo = uut.repository

        assert_equals("synthetic", repo.type)
        assert_equals(join("/path/misuse", "compile"), repo.url)

    def test_fix_revision(self):
        uut = TMisuse(meta={"fix": {"revision": 42}})

        assert_equals(42, uut.fix_revision)

    def test_no_fix_revision(self):
        uut = TMisuse(meta={"fix": {}})

        assert_equals(None, uut.fix_revision)

    def test_finds_no_pattern(self):
        uut = Misuse(self.temp_dir)

        assert uut.patterns == set()

    def test_finds_single_pattern(self):
        uut = Misuse(self.temp_dir)

        pattern_dir = join(self.temp_dir, "patterns")
        makedirs(pattern_dir)
        pattern_file = join(pattern_dir, "APattern.java")
        self.create_file(pattern_file)

        assert_equals(uut.patterns, {Pattern(pattern_file)})

    def test_finds_multiple_patterns(self):
        uut = Misuse(self.temp_dir)

        pattern_dir = join(self.temp_dir, "patterns")
        makedirs(pattern_dir)
        pattern1_file = join(pattern_dir, "OnePattern.java")
        self.create_file(pattern1_file)
        pattern2_file = join(pattern_dir, "AnotherPattern.java")
        self.create_file(pattern2_file)

        assert_equals(uut.patterns, {Pattern(pattern1_file), Pattern(pattern2_file)})

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
    def create_file(path: str):
        open(path, 'a').close()


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
