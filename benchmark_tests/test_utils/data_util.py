from typing import Any, Dict, List

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion


def create_project(project_id: str, base_path: str = "-test-/-path-", yaml: Dict[str, Any] = None,
                   versions: List[ProjectVersion] = None):
    project = Project(base_path, project_id)
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
    misuse._YAML = {"location": {"file": "-dummy-/-file-", "method": "-method-()"}}
    if yaml is not None:
        misuse._YAML.update(yaml)
    return misuse
