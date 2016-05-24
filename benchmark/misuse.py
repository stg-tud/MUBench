import yaml
from os import listdir
from os.path import isdir, isfile, join, basename
from typing import Set

class Misuse:
    META_FILE = "meta.yml"
    
    @staticmethod
    def ismisuse(path: str) -> bool:
        return isdir(path) and isfile(join(path, Misuse.META_FILE))
    
    def __init__(self, path: str):
        self.path = path
        self.name = basename(path)
        self.meta_file = join(path, Misuse.META_FILE)
    
    @property
    def project_name(self) -> str:
        project_name = self.name
        if '.' in project_name:
            project_name = project_name.split('.', 1)[0]
        return project_name
    
    @property
    def pattern(self) -> Set[str]:
        pattern_path = join(self.path, "pattern")
        if isdir(pattern_path):
            return set([join(pattern_path, file) for file in listdir(pattern_path)])
        else:
            return set()
    
    @property
    def meta(self):
        if getattr(self, '_META', None) is None:
            stream = open(self.meta_file, 'r')
            try:
                self._META = yaml.load(stream)
            finally:
                stream.close()
        return self._META
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.path == other.path
    
    def __ne__(self, other):
        return not self.__eq__(other)
