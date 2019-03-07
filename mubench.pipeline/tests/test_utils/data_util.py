from typing import Any, Dict, List

from data.correct_usage import CorrectUsage
from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion


def create_project(project_id: str, base_path: str = "", meta: Dict[str, Any] = None):
    project = Project(base_path, project_id)
    project._YAML = meta
    return project


def create_version(version_id: str, misuses: List[Misuse] = None, meta: Dict[str, Any] = None, project: Project=None):
    if not project:
        project = create_project("-project-")
    version = ProjectVersion(project._base_path, project.id, version_id)
    version._ProjectVersion__project = project
    version._MISUSES = [create_misuse("-misuse-")] if misuses is None else misuses
    version._YAML = meta
    project._VERSIONS.append(version)
    return version


def create_misuse(misuse_id: str, meta: Dict[str, Any] = None, project: Project = None, version: ProjectVersion = None,
                  correct_usages: List[CorrectUsage] = None):
    if not project:
        project = create_project("-project-")
    if not version:
        version = create_version("-version-", misuses=[])
    misuse = Misuse(project._base_path, project.id, version.version_id, misuse_id)
    misuse._Misuse__project = project
    misuse._YAML = {"location": {"file": "-dummy-/-file-", "method": "-method-()"}}
    misuse._CORRECT_USAGES = correct_usages if correct_usages else []
    if meta:
        misuse._YAML.update(meta)

    version._MISUSES.append(misuse)
    return misuse
