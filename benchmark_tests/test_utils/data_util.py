from typing import Any, Dict, List

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion


def create_project(path: str, versions: List[ProjectVersion] = None, yaml: Dict[str, Any] = None):
    project = Project(path)
    project._VERSIONS = [] if versions is None else versions
    project._YAML = {} if yaml is None else yaml
    return project


def create_version(path: str, misuses: List[Misuse] = None, yaml: Dict[str, Any] = None):
    version = ProjectVersion(path)
    version._MISUSES = [] if misuses is None else misuses
    version._YAML = {} if yaml is None else yaml
    return version


def create_misuse(path: str, yaml: Dict[str, Any] = None):
    misuse = Misuse(path)
    misuse._YAML = {} if yaml is None else yaml
    return misuse
