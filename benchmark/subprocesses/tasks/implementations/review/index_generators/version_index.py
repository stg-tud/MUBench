from os import listdir
from os.path import isdir, join

from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import safe_write


def generate(version_folder: str, version_findings_folder: str, project: Project, version: ProjectVersion):
    lines = []

    versions = [version for version in listdir(version_findings_folder) if
                isdir(join(version_findings_folder, version))]
    for version in versions:
        detector_link_paragraph = '<p><a href="{0}/review.html">{0}</a></p>'.format(version)
        lines.append(detector_link_paragraph)

        safe_write('\n'.join(lines), join(version_folder, 'index.html'), False)
