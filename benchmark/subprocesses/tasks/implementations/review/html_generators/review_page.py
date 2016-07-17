from textwrap import wrap
from typing import Dict
from typing import List

from os.path import join

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import safe_write


def generate(review_folder: str, findings_folder: str, detector: str, project: Project, version: ProjectVersion,
             misuse: Misuse, potential_hits: List[Dict[str, str]]):
    lines = []

    lines.append("<p>Reviewing: {}/{}/{}/{}<hr></p>".format(detector, project.id, version.version_id, misuse.id))

    lines.append("<p>{}</p>".format(__multiline(misuse.description)))
    lines.append("<p>{}</p>".format(__multiline(misuse.fix.description)))

    lines.append("<p>Characteristics:<br/>".format(misuse.characteristics))
    for characteristic in misuse.characteristics:
        lines.append(" - {}<br/>".format(characteristic))
    lines.append("</p>")

    lines.append("<p>In {}.{}</p>".format(misuse.location.file, misuse.location.method))
    lines.append("<hr>")

    lines.append("Potential Hits<br/>")
    lines.extend(__generate_table(potential_hits))

    safe_write('\n'.join(lines), join(review_folder, 'review.html'), False)


def __multiline(text: str):
    return "<br/>".join(wrap(text, width=80))


def __generate_table(potential_hits):
    table_lines = ["<table border=\"1\" cellpadding=\"5\">"]

    keys = set()
    for potential_hit in potential_hits:
        keys.update(potential_hit.keys())
    keys = sorted(keys)

    table_lines.append("<tr>")
    for key in keys:
        table_lines.append("<th>{}</th>".format(key))
    table_lines.append("</tr>")

    for potential_hit in potential_hits:
        table_lines.append("<tr>")
        for key in keys:
            table_lines.append("<td>{}</td>".format(potential_hit.get(key, "")))
        table_lines.append("</tr>")

    table_lines.append("</table>")

    return table_lines
