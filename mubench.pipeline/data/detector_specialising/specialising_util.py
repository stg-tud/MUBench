from base64 import urlsafe_b64encode
from os import makedirs, remove
from os.path import join, exists, dirname

from utils.io import safe_write
from utils.shell import Shell

__DOT_CONVERSION_TIME_LIMIT = 900


def format_float_value(finding, float_key):
    finding[float_key] = str(round(float(finding[float_key]), 3))


def replace_dot_graph_with_image(finding, key, base_path) -> str:
    image_name = "{}-{}.svg".format(__get_id(finding), __filename_encode(key))
    try:
        __create_image(finding[key], base_path, image_name)
        finding[key] = image_name
        return join(base_path, image_name)
    except TimeoutError:
        finding[key] = "Generating DOT image was aborted, since it took longer than {} minutes. The resulting graph " \
                       "would likely be unreadable anyways...".format(__DOT_CONVERSION_TIME_LIMIT / 60)
        return join(dirname(__file__), "empty_dummy_dot.png")


def __get_id(finding):
    if "misuse" in finding:
        return "{}-{}".format(finding["misuse"], finding["rank"])
    else:
        return "f{}".format(finding["rank"])


def __filename_encode(key):
    return urlsafe_b64encode(bytes(key, "utf-8")).decode("utf-8")


def __create_image(dot_graph, working_directory, image_name):
    image_path = join(working_directory, image_name)
    if not exists(image_path):
        makedirs(working_directory, exist_ok=True)
        dot_path = image_path + ".dot"
        safe_write(dot_graph, dot_path, append=False)
        Shell.exec("dot -v -Tsvg -o'{}' '{}'".format(image_path, dot_path), timeout=__DOT_CONVERSION_TIME_LIMIT)
        remove(dot_path)
