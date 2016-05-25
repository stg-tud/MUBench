import yaml
from typing import Dict, Union
from os import makedirs
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.misuse import Misuse
from benchmark.utils.io import safe_write

class TMisuse(Misuse):
    def __init__(self, path: str = ":irrelevant:", meta: Dict[str, Union[str, Dict]] = {}):
        Misuse.__init__(self, path)
        self._META = meta

class TestMisuse:
    
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-misuse.')
    
    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)
    
    def test_extacts_name(self):
        uut = Misuse("/MUBench/data/project.id")
        assert uut.name == "project.id"
    
    def test_finds_meta_file(self):
        uut = Misuse("MUBench/data/project.id")
        assert uut.meta_file == "MUBench/data/project.id/meta.yml"
    
    def test_extracts_project_name(self):
        uut = Misuse(join("C:", "my-path", "project.42-2"))
        assert "project" == uut.project_name

    def test_extracts_synthetic_project_name(self):
        uut = Misuse((join("C:", "my-path", "synthetic-example")))
        assert "synthetic-example" == uut.project_name
    
    def test_reads_meta_file(self):
        uut = Misuse(self.temp_dir)
        
        safe_write(yaml.dump({'key' : 'value'}), uut.meta_file, append=False)
        
        assert uut.meta['key'] == 'value'
    
    def test_repository(self):
        uut = TMisuse(meta = {"fix" : {"repository": {"type" : "git", "url": "ssh://foobar.git"}}})
        repo = uut.repository

        assert_equals("git", repo.type)
        assert_equals("ssh://foobar.git", repo.url)
    
    def test_synthetic_repository(self):
        uut = TMisuse("/path/misuse", {"fix" : {"repository": {"type" : "synthetic"}}})
        repo = uut.repository

        assert_equals("synthetic", repo.type)
        assert_equals("/path/misuse/compile", repo.url)
    
    def test_fix_revision(self):
        uut = TMisuse(meta = {"fix": {"revision": 42}})
        
        assert_equals(42, uut.fix_revision)
    
    def test_no_fix_revision(self):
        uut = TMisuse(meta = {"fix": {}})
        
        assert_equals(None, uut.fix_revision)
    
    def test_finds_no_pattern(self):
        uut = Misuse(self.temp_dir)
        
        assert uut.pattern == set()
    
    def test_finds_single_pattern(self):
        uut = Misuse(self.temp_dir)
        
        pattern_dir = join(self.temp_dir, "pattern")
        makedirs(pattern_dir)
        pattern_file = join(pattern_dir, "APattern.java")
        self.create_file(pattern_file)
        
        assert uut.pattern == {pattern_file}
    
    def test_finds_multiple_patterns(self):
        uut = Misuse(self.temp_dir)
        
        pattern_dir = join(self.temp_dir, "pattern")
        makedirs(pattern_dir)
        pattern1_file = join(pattern_dir, "OnePattern.java")
        self.create_file(pattern1_file)
        pattern2_file = join(pattern_dir, "AnotherPattern.java")
        self.create_file(pattern2_file)
        
        assert uut.pattern == {pattern1_file, pattern2_file}
    
    def test_equals_by_path(self):
        assert Misuse("foo/bar") == Misuse("foo/bar")
    
    def test_differs_by_path(self):
        assert Misuse("foo/bar") != Misuse("bar/bazz")
    
    def create_file(self, path: str):
        open(path, 'a').close()
