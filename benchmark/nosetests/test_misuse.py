import yaml
from typing import Dict, Union
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from benchmark.misuse import Misuse
from benchmark.utils.io import safe_write

class TMisuse(Misuse):
    def __init__(self, path: str, meta: Dict[str, Union[str, Dict]]):
        Misuse.__init__(self, path)
        self._META = meta

class TestMisuse:
    
    def test_extacts_name(self):
        uut = TMisuse("/MUBench/data/project.id", {})
        assert uut.name == "project.id"
    
    def test_finds_meta_file(self):
        uut = TMisuse("MUBench/data/project.id", {})
        assert uut.meta_file == "MUBench/data/project.id/meta.yml"
    
    def test_project_name(self):
        uut = TMisuse(join("C:", "my-path", "project.42-2"), {})
        assert "project" == uut.project_name

    def test_synthetic_project_name(self):
        uut = TMisuse((join("C:", "my-path", "synthetic-example")), {})
        assert "synthetic-example" == uut.project_name
    
    def test_read_meta_file(self):
        self.temp_dir = mkdtemp(prefix='mubench-misuse.')
        try:
            safe_write(yaml.dump({'key' : 'value'}), join(self.temp_dir, "meta.yml"), append=False)
            
            uut = Misuse(self.temp_dir)
            assert uut.meta['key'] == 'value'
        finally:
            rmtree(self.temp_dir, ignore_errors=True)
    
    def test_equals_by_path(self):
        assert TMisuse("foo/bar", {}) == TMisuse("foo/bar", {})
    
    def test_not_equal_by_path(self):
        assert TMisuse("foo/bar", {}) != TMisuse("bar/bazz", {})