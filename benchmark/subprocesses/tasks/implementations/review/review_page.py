import html
from os.path import join
from textwrap import wrap
from typing import Dict
from typing import List

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.implementations.review import potential_hits_section
from benchmark.utils.io import safe_write
from benchmark.utils.java_utils import exec_util
from benchmark.utils.shell import CommandFailedError


def generate(review_folder: str, detector: str, compiles_path: str, project: Project, version: ProjectVersion,
             misuse: Misuse, potential_hits: List[Dict[str, str]]):
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
             '<p>{}</p>'.format(__get_target_code(compiles_path, version, misuse.location.file, misuse.location.method)),
             '<h2>Potential Hits</h2>'] + potential_hits_section.generate(detector, potential_hits)

    safe_write('\n'.join(lines), join(review_folder, 'review.html'), False)


def generate2(review_file: str, detector: str, compiles_path: str, version: ProjectVersion, finding: Dict[str,str]):
    review = """
        <h1>Review</h1>
        <table>
            <tr><td><b>Detector:</b></td><td>{}</td></tr>
            <tr><td><b>Target:</b></td><td>{}</td></tr>
            <tr><td><b>Finding:</b></td><td>{}</td></tr>
            <tr><td><b>In File:</b></td><td>{}</td></tr>
            <tr><td><b>In Method:</b></td><td>{}</td></tr>
        </table>
        <p>{}</p>
        {}
        """.format(detector, version, finding["id"], join(version.source_dir, finding["file"]), finding["method"],
                   __get_target_code(compiles_path, version, finding["file"], finding["method"]),
                   "\n".join(potential_hits_section.generate(detector, [finding])))

    safe_write(review, review_file, False)


def __get_target_code(compiles_path: str, version: ProjectVersion, file: str, method: str) -> str:
    version_compile = version.get_compile(compiles_path)
    misuse_file = join(version_compile.original_sources_path, file)

    try:
        method = exec_util("MethodExtractor", "\"{}\" \"{}\"".format(misuse_file, method))
    except CommandFailedError as e:
        method = str(e)

    return '<script src="https://cdn.rawgit.com/google/code-prettify/master/loader/run_prettify.js' \
           '?autoload=true&amp;skin=sunburst"></script>\n' \
           '<pre class="prettyprint"><code class="language-java">{}</code></pre>'.format(html.escape(method))


def __multiline(text: str):
    return "<br/>".join(wrap(text, width=120))
