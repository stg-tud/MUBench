import os

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from utils.io import safe_open


class CrossProjectCreateIndexTask:
    def __init__(self, index_file: str):
        self.index_file = index_file

        if os.path.exists(index_file):
            os.remove(index_file)

    def run(self, project: Project, version: ProjectVersion, misuse: Misuse):
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(project.id, version.version_id, misuse.misuse_id,
                                                  ':'.join(version.source_dirs),
                                                  misuse.location.file, misuse.location.method,
                                                  "\t".join(misuse.apis)), file=safe_open(self.index_file + '-' + version.id, "a"))
