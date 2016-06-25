import yaml
from os import listdir
from os.path import join, exists, isdir, basename
from typing import List, Dict, Any, Optional

from benchmark.data.project_checkout import ProjectCheckout, GitProjectCheckout, SVNProjectCheckout, \
    LocalProjectCheckout
from benchmark.data.project_compile import ProjectCompile
from benchmark.data.project_version import ProjectVersion


# noinspection PyAttributeOutsideInit
class Project:
    PROJECT_FILE = 'project.yml'

    class Repository:
        def __init__(self, vcstype: Optional[str], url: Optional[str]):
            self.vcstype = vcstype  # type: Optional[str]
            self.url = url  # type: Optional[str]

    def __init__(self, path: str):
        self._path = path  # type: str
        self._versions_path = join(path, "versions")  # type: str
        self._project_file = join(path, Project.PROJECT_FILE)  # type: str

    @staticmethod
    def validate(path: str) -> bool:
        return exists(join(path, Project.PROJECT_FILE))

    @property
    def _yaml(self) -> Dict[str, Any]:
        if getattr(self, '_YAML', None) is None:
            with open(self._project_file) as project_file:
                project_yml = yaml.load(project_file)
            self._YAML = project_yml
        return self._YAML

    @property
    def id(self):
        return basename(self._path)

    @property
    def name(self) -> Optional[str]:
        return self._yaml.get("name", None)

    @property
    def repository(self) -> Repository:
        repository = self._yaml.get("repository", None)
        if repository is None:
            return None

        repository_type = repository.get("type", None)
        repository_url = repository.get("url", None)

        return Project.Repository(repository_type, repository_url)

    @property
    def versions(self) -> List[ProjectVersion]:
        if getattr(self, '_VERSIONS', None) is None:
            versions = list()  # type: List[ProjectVersion]

            versions_path = self._versions_path
            if exists(versions_path):
                version_dirs = [join(versions_path, subdir) for subdir in listdir(versions_path) if
                                isdir(join(versions_path, subdir))]

                for version_dir in version_dirs:
                    if ProjectVersion.validate(version_dir):
                        versions.append(ProjectVersion(version_dir))

            self._VERSIONS = versions

        return self._VERSIONS

    def get_checkout(self, version: ProjectVersion, base_path: str) -> ProjectCheckout:
        repository = self.repository
        if repository.vcstype == "git":
            url = repository.url
            revision = version.revision + "~1"
            return GitProjectCheckout(url, base_path, self.id, str(version), revision)
        elif repository.vcstype == "svn":
            url = repository.url
            revision = str(int(version.revision) - 1)
            return SVNProjectCheckout(url, base_path, self.id, str(version), revision)
        elif repository.vcstype == "synthetic":
            url = join(self._path, "versions", "0", "compile")
            return LocalProjectCheckout(url, base_path, self.id)
        else:
            raise ValueError("unknown repository type: {}".format(repository.vcstype))

    def get_compile(self, version: ProjectVersion, base_path: str) -> ProjectCompile:
        if version:
            base_path = join(base_path, self.id, str(version))
        else:
            base_path = join(base_path, self.id)
        return ProjectCompile(base_path)

    @staticmethod
    def get_projects(data_path: str) -> List['Project']:
        if not exists(data_path):
            return []

        subfolders = [join(data_path, content) for content in listdir(data_path) if isdir(join(data_path, content))]
        projects = []
        for subfolder in subfolders:
            if Project.validate(subfolder):
                projects.append(Project(subfolder))

        return projects
