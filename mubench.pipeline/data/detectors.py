from importlib import import_module
from os import listdir

from os.path import isdir, join
from typing import List

import sys


def find_detector(detectors_path: str, detector_id_prefix: str, java_options: List[str]):
    detector_id = _find_detector_id(detector_id_prefix, detectors_path)
    detector_id_short = detector_id.split("_", 1)[0]

    sys.path.insert(0, detectors_path)
    try:
        module = import_module("{}.{}".format(detector_id, detector_id_short))
        detector_class = getattr(module, detector_id_short)
        detector_instance = detector_class(detectors_path, detector_id, java_options)
    finally:
        sys.path.pop(0)
    return detector_instance


def _find_detector_id(detector_id_prefix, detectors_path) -> str:
    available_detector_ids = get_available_detector_ids(detectors_path)
    detector_ids = [id for id in available_detector_ids if id == detector_id_prefix] or\
                   [id for id in available_detector_ids if id.startswith(detector_id_prefix)]
    if not detector_ids:
        raise ValueError("no detector with id '{}'".format(detector_id_prefix))
    elif len(detector_ids) > 1:
        raise ValueError("more than one detector matching id prefix '{}': {}".format(detector_id_prefix, detector_ids))
    else:
        return detector_ids[0]


def get_available_detector_ids(detectors_path):
    return [dir_name for dir_name in listdir(detectors_path) if isdir(join(detectors_path, dir_name))]
