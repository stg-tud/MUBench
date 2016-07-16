from os import listdir

from os.path import join, isdir

from benchmark.utils.io import safe_write


def generate(review_folder: str):
    lines = []

    detectors = [detector for detector in listdir(review_folder) if isdir(join(review_folder, detector))]
    for detector in detectors:
        detector_link_paragraph = '<p><a href="{0}/index.html">{0}</a></p>'.format(detector)
        lines.append(detector_link_paragraph)

    safe_write('\n'.join(lines), join(review_folder, 'index.html'), False)
