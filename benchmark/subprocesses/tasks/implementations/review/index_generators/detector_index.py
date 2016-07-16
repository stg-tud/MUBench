from os import listdir

from os.path import isdir

from os.path import join

from benchmark.utils.io import safe_write


def generate(detector_review_folder: str, detector_findings_folder: str):
    lines = []

    versions = [version for version in listdir(detector_findings_folder) if
                isdir(join(detector_findings_folder, version))]
    for version in versions:
        detector_link_paragraph = '<p><a href="{0}/index.html">{0}</a></p>'.format(version)
        lines.append(detector_link_paragraph)

    safe_write('\n'.join(lines), join(detector_review_folder, 'index.html'), False)
