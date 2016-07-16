from os import listdir
from os.path import join, isdir
from typing import List

from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import safe_open


def generate_main_index(review_folder: str):
    lines = []

    detectors = [detector for detector in listdir(review_folder) if isdir(join(review_folder, detector))]
    for detector in detectors:
        detector_link_paragraph = '<p><a href="{0}/index.html">{0}</a></p>'.format(detector)
        lines.append(detector_link_paragraph)

    __write_lines_to_file(join(review_folder, 'index.html'), lines)


def generate_detector_index(detector_folder: str):
    lines = []

    versions = [version for version in listdir(detector_folder) if isdir(join(detector_folder, version))]
    for version in versions:
        detector_link_paragraph = '<p><a href="{0}/index.html">{0}</a></p>'.format(version)
        lines.append(detector_link_paragraph)

    __write_lines_to_file(join(detector_folder, 'index.html'), lines)


def generate_project_index(project_folder: str, project: Project):
    lines = []

    versions = [version for version in listdir(project_folder) if isdir(join(project_folder, version))]
    for version in versions:
        detector_link_paragraph = '<p><a href="{0}/index.html">{0}</a></p>'.format(version)
        lines.append(detector_link_paragraph)

    __write_lines_to_file(join(project_folder, 'index.html'), lines)


def generate_version_index(version_folder: str, project: Project, version: ProjectVersion):
    lines = []

    versions = [version for version in listdir(version_folder) if isdir(join(version_folder, version))]
    for version in versions:
        detector_link_paragraph = '<p><a href="{0}/review.html">{0}</a></p>'.format(version)
        lines.append(detector_link_paragraph)

    __write_lines_to_file(join(version_folder, 'index.html'), lines)


def __write_lines_to_file(file: str, lines: List[str]):
    with safe_open(file, 'w+') as stream:
        for line in lines:
            print(line, file=stream)
