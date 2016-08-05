from pydoc import html
from typing import Dict
from typing import List


def generate(detector: str, potential_hits: List[Dict[str, str]]) -> List[str]:
    generate = globals().get(detector, globals()['default'])
    return generate(potential_hits)


def default(potential_hits: List[Dict[str, str]]):
    table_lines = ["<table border=\"1\" cellpadding=\"5\">"]

    keys = set()
    for potential_hit in potential_hits:
        keys.update(potential_hit.keys())
    keys.discard("file")
    keys.discard("method")
    keys.discard("id")
    keys = ["id"] + sorted(keys)

    table_lines.append("<tr>")
    for key in keys:
        table_lines.append("<th>{}</th>".format(key))
    table_lines.append("</tr>")

    for potential_hit in potential_hits:
        table_lines.append("<tr>")
        for key in keys:
            value = potential_hit.get(key, "")
            if type(value) is str:
                if value.startswith("<img"):
                    table_lines.append("<td>{}</td>".format(value))
                else:
                    table_lines.append("<td>{}</td>".format(html.escape(value)))
            elif type(value) is int:
                table_lines.append("<td>{}</td>".format(html.escape(str(value))))
            elif type(value) is list:
                table_lines.append("<td><ul>")
                for elm in value:
                    table_lines.append("<li>{}</li>".format(html.escape(elm)))
                table_lines.append("</ul></td>")
            else:
                raise ValueError("unexpected value type '{}'".format(type(value)))
        table_lines.append("</tr>")

    table_lines.append("</table>")

    return table_lines


def grouminer(potential_hits: List[Dict[str, str]]):
    return default(potential_hits)  # TODO: add handling for dot graphs
