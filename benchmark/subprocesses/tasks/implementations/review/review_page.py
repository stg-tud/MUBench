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
    review = """
        <h1>Review</h1>
        <table>
            <tr><td><b>Detector:</b></td><td>{}</td></tr>
            <tr><td><b>Target:</b></td><td>{}</td></tr>
            <tr><td><b>Misuse:</b></td><td>{}</td></tr>
        </table>
        <h2>Misuse Details</h2>
        <p>Details about the known misuse from the MUBench dataset.</p>
        <table class="fw">
            <tr><td class="vtop"><b>Description:</b></td><td>{}</td></tr>
            <tr><td class="vtop"><b>Fix Description:</b></td><td>{} (<a href="{}">see diff</a>)</td></tr>
            <tr><td class="vtop"><b>Violation Types:</b></td><td>{}</td></tr>
            <tr><td><b>In File:</b></td><td>{}</td></tr>
            <tr><td><b>In Method:</b></td><td>{}</td></tr>
            <tr><td class="vtop"><b>Code with Misuse:</b></td><td>{}</td></tr>
        </table>
        <h2>Potential Hits</h2>
        <p>Findings of the detector that identify an anomaly in the same file and method as the known misuse.
            Please reviews whether any of these findings actually correspond to the kown misuse.</p>
        {}
        """.format(detector, version, misuse,
                   __multiline(misuse.description),
                   __multiline(misuse.fix.description),
                   misuse.fix.commit,
                   __list(misuse.characteristics),
                   misuse.location.file, misuse.location.method,
                   __get_target_code(compiles_path, version, misuse.location.file, misuse.location.method),
                   "\n".join(potential_hits_section.generate(detector, potential_hits)))

    safe_write(__get_page(review), join(review_folder, 'review.html'), False)


def generate2(review_file: str, detector: str, compiles_path: str, version: ProjectVersion, finding: Dict[str,str]):
    review = """
        <h1>Review</h1>
        <table>
            <tr><td><b>Detector:</b></td><td>{}</td></tr>
            <tr><td><b>Target:</b></td><td>{}</td></tr>
        </table>
        <h2>Potential Misuse</h2>
        <p>Anomaly identified by the detector.
            Please review whether this anomaly corresponds to a misuse.</p>
        <table class="fw">
            <tr><td><b>Finding:</b></td><td>{}</td></tr>
            <tr><td><b>In File:</b></td><td>{}</td></tr>
            <tr><td><b>In Method:</b></td><td>{}</td></tr>
            <tr><td class="vtop"><b>Code with Finding:</b></td><td>{}</td></tr>
            <tr><td class="vtop"><b>Metadata:</b></td><td>{}</td></tr>
        </table>
        """.format(detector, version,
                   finding["id"], join(version.source_dir, finding["file"]), finding["method"],
                   __get_target_code(compiles_path, version, finding["file"], finding["method"]),
                   "\n".join(potential_hits_section.generate(detector, [finding])))

    safe_write(__get_page(review), review_file, False)


def __get_page(content: str):
    return """
        <html>
            <head>
                <style>{}</style>
            </head>
            <body>
            {}
            </body>
        </html>
    """.format(__get_css(), content)


def __get_css():
    return """
        table.fw {width:100%;}
        .vtop {vertical-align:top}
        .prettyprint ol.linenums > li { list-style-type: decimal; }
        """


def __get_target_code(compiles_path: str, version: ProjectVersion, file: str, method: str) -> str:
    version_compile = version.get_compile(compiles_path)
    misuse_file = join(version_compile.original_sources_path, file)

    code = """<script src="https://cdn.rawgit.com/google/code-prettify/master/loader/run_prettify.js?autoload=true&amp;skin=sunburst"></script>"""
    snippet = """<pre class="prettyprint linenums:{}"><code class="language-java">{}</code></pre>"""

    try:
        output = exec_util("MethodExtractor", "\"{}\" \"{}\"".format(misuse_file, method)).strip("\n")
        if output:
            methods = output.split("\n===\n")
            for method in methods:
                # comes as "<first-line number>:<declaring type>:<code>
                info = method.split(":", 2)
                code += snippet.format(int(info[0]) - 1,
                                       """class {} {{\n{}\n}}""".format(info[1], html.escape(info[2].strip("\n"))))
    except CommandFailedError as e:
        code += snippet.format(1, html.escape(str(e)))

    return code


def __multiline(text: str):
    return "<br/>".join(wrap(text, width=120))


def __list(l: List):
    return """
        <ul>
            <li>{}</li>
        </ul>
        """.format("</li>\n            <li>".join(l))
