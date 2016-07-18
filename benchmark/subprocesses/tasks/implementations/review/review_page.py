import html
from textwrap import wrap
from typing import Dict
from typing import List

from os.path import join

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import safe_write


def generate(review_folder: str, detector: str, project: Project, version: ProjectVersion,
             misuse: Misuse, potential_hits: List[Dict[str, str]]):
    lines = ["<h1>Review: {}/{}/{}/{}</h1>".format(detector, project.id, version.version_id, misuse.id),
             "<h2>Misuse Details</h2>",
             "<p><b>Description:</b> {}</p>".format(__multiline(misuse.description)),
             "<p><b>Fix Description:</b> {}</p>".format(__multiline(misuse.fix.description)),
             "<p><b>Misuse Elements:</b><ul>".format(misuse.characteristics)]

    for characteristic in misuse.characteristics:
        lines.append("<li>{}</li>".format(characteristic))
    lines.append("</ul></p>")

    lines.append("<p><b>In File:</b> <a href=\"{}\">{}</a>, <b>Method:</b> {}</p>"
                 .format(misuse.fix.commit, misuse.location.file, misuse.location.method))

    lines.append("<h2>Potential Hits</h2>")
    lines.extend(__generate_table(potential_hits))

    safe_write('\n'.join(lines), join(review_folder, 'review.html'), False)


def __multiline(text: str):
    return "<br/>".join(wrap(text, width=120))


def __generate_table(potential_hits):
    table_lines = ["<table border=\"1\" cellpadding=\"5\">"]

    keys = set()
    for potential_hit in potential_hits:
        keys.update(potential_hit.keys())
    keys.discard("file")
    keys.discard("method")
    keys = sorted(keys)

    table_lines.append("<tr>")
    for key in keys:
        table_lines.append("<th>{}</th>".format(key))
    table_lines.append("</tr>")

    for potential_hit in potential_hits:
        table_lines.append("<tr>")
        for key in keys:
            value = potential_hit.get(key, "")
            if type(value) is str:
                table_lines.append("<td>{}</td>".format(html.escape(value)))
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
