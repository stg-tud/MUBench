from os import listdir
from os.path import isdir
from os.path import join

from benchmark.data.project import Project
from benchmark.utils.io import safe_write


def generate(project_folder: str, project: Project):
    lines = []

    versions = [version for version in listdir(project_folder) if isdir(join(project_folder, version))]
    for version in versions:
        detector_link_paragraph = '<p><a href="{0}/index.html">{0}</a></p>'.format(version)
        lines.append(detector_link_paragraph)

        safe_write('\n'.join(lines), join(project_folder, 'index.html'), False)
