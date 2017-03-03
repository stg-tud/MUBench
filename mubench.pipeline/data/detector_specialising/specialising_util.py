from os import makedirs, remove

from os.path import join, exists

from utils.io import safe_write
from utils.shell import Shell


def format_float_value(finding, float_key):
    finding[float_key] = str(round(float(finding[float_key]), 3))


def replace_dot_graph_with_image(finding, key, base_path) -> str:
    image_name = "f{}-{}.png".format(finding["rank"], key)
    __create_image(finding[key], base_path, image_name)
    finding[key] = image_name
    return join(base_path, image_name)


def __create_image(dot_graph, working_directory, image_name):
    image_path = join(working_directory, image_name)
    if not exists(image_path):
        makedirs(working_directory, exist_ok=True)
        dot_path = image_path + ".dot"
        safe_write(dot_graph, dot_path, append=False)
        Shell.exec("dot -Tpng -o\"{}\" \"{}\"".format(image_path, dot_path))
        remove(dot_path)
