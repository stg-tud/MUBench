import html
from textwrap import wrap
from typing import Dict, Callable
from typing import List

from os.path import join

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import safe_write

potential_hits_section_generators = {}  # type: Dict[str, Callable[[List[Dict[str, str]]], List[str]]]


def generate(review_folder: str, detector: str, project: Project, version: ProjectVersion, misuse: Misuse,
             potential_hits: List[Dict[str, str]]):
    lines = ['<h1>Review: {}/{}/{}/{}</h1>'.format(detector, project.id, version.version_id, misuse.id),
             '<h2>Misuse Details</h2>',
             '<p><b>Description:</b> {}</p>'.format(__multiline(misuse.description)),
             '<p><b>Fix Description:</b> {}</p>'.format(__multiline(misuse.fix.description)),
             '<p><b>Misuse Elements:</b><ul>'] + \
            ['<li>{}</li>'.format(characteristic) for characteristic in misuse.characteristics] + \
            ['</ul></p>',
             '<p><b>In File:</b> <a href="{}">{}</a>, <b>Method:</b> {}</p>'.format(
                 misuse.fix.commit,
                 misuse.location.file,
                 misuse.location.method),
             '<p>{}</p>'.format(__get_target_code(project, version, misuse)),
             '<h2>Potential Hits</h2>'] + __generate_potential_hits_section(detector, potential_hits)

    safe_write('\n'.join(lines), join(review_folder, 'review.html'), False)


def __get_target_code(project: Project, version: ProjectVersion, misuse: Misuse) -> str:
    misuse_file = join('checkouts', project.id, version.version_id,
                       'original-src', misuse.location.file)  # TODO: pass hardcoded parts as arguments?
    with open(misuse_file) as file:
        code = file.read()
    method = __get_method_code(misuse, code)
    return '<script src="https://cdn.rawgit.com/google/code-prettify/master/loader/run_prettify.js' \
           '?autoload=true&amp;skin=sunburst"></script>\n' \
           '<pre class="prettyprint"><code class="language-java">{}</code></pre>'.format(html.escape(method))


def __get_method_code(misuse: Misuse, code: str):
    return code

    # TODO: this doesn't work...
    # Sometimes javadoc or other comments in the file contain the method signature.
    # We would need to parse the actual Java Code to get the correct snippet.
    #
    # name = misuse.location.method
    # split = code.split(name, 1)
    # if len(split) < 2:
    #     # sometimes parameters are declared as final
    #     name_without_parameters = name.split('(', 1)[0]
    #     split = code.split(name_without_parameters, 1)
    #     if len(split) < 2:
    #         return code  # fallback
    #
    # substring = split[1]
    #
    # body = ''
    #
    # in_method = False
    # depth = 0
    # for char in substring:
    #     body += char
    #
    #     if char == '{':
    #         in_method = True
    #         depth += 1
    #     if char == '}':
    #         depth -= 1
    #
    #     if in_method and depth == 0:
    #         break
    #
    # return name + body


def __generate_potential_hits_section(detector: str, potential_hits: List[Dict[str, str]]) -> List[str]:
    generate_section = potential_hits_section_generators.get(detector) or __default_generate_potential_hits_section
    return generate_section(potential_hits)


def __default_generate_potential_hits_section(potential_hits: List[Dict[str, str]]) -> List[str]:
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


def __multiline(text: str):
    return "<br/>".join(wrap(text, width=120))
