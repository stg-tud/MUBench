from os import makedirs

from os.path import dirname, join

from benchmark.utils.shell import Shell


def format_float_value(finding, float_key):
    finding[float_key] = str(round(float(finding[float_key]), 3))


def replace_dot_graph_with_image(finding, key, base_path) -> str:
    image_name = "f{}-{}.png".format(finding["id"], key)
    __create_image(finding[key], join(base_path, image_name))
    finding[key] = image_name
    return join(base_path, image_name)


def __create_image(dot_graph, file):
    makedirs(dirname(file), exist_ok=True)
    Shell.exec("""echo "{}" | dot -Tpng -o"{}" """.format(dot_graph.replace("\\", "\\\\").replace("\"", "\\\""), file))
