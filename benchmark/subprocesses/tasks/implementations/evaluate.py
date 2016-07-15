import logging
from os.path import join
from textwrap import wrap
from typing import Dict, Iterable

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.subprocesses.tasks.implementations.detect import Run
from benchmark.utils.io import safe_open, write_yaml


class Evaluate(ProjectVersionMisuseTask):
    no_hit = 0
    potential_hit = 1

    def __init__(self, results_path: str, detector_result_file: str, checkout_base_dir: str, eval_result_file: str):
        super().__init__()
        self.results_path = results_path
        self.detector_result_file = detector_result_file
        self.checkout_base_dir = checkout_base_dir
        self.eval_result_file = eval_result_file

        self.results = []

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        logger = logging.getLogger("evaluate")
        logger.debug("Checking hit for %s in %s...", misuse, version)

        result_path = join(self.results_path, project.id, version.version_id)
        detector_run = Run(result_path)

        findings = detector_run.findings
        potential_hits = Evaluate.__find_potential_hits(findings, misuse)

        if potential_hits:
            logger.info("Found potential hit for %s.", misuse)
            self.results.append((misuse.id, Evaluate.potential_hit))
        else:
            logger.info("No hit for %s.", misuse)
            self.results.append((misuse.id, Evaluate.no_hit))

        misuse_finding_path = join(result_path, misuse.id)
        remove_tree(misuse_finding_path)
        write_yaml({"misuse": {"description": Evaluate.__multiline(misuse.description),
                               "location": {"file": misuse.location.file, "method": misuse.location.method}},
                    "fix": {"description": Evaluate.__multiline(misuse.fix.description),
                            "commit": misuse.fix.commit},
                    "findings": potential_hits}, file=join(misuse_finding_path, "finding.yml"))

        return Response.ok

    def teardown(self):
        with safe_open(join(self.results_path, self.eval_result_file), 'w+') as file_result:
            for result in self.results:
                print(str(result).lstrip('(').rstrip(')'), file=file_result)

    @staticmethod
    def __find_potential_hits(findings: Iterable[Dict[str, str]], misuse: Misuse) -> bool:
        logger = logging.getLogger("evaluate.compare")
        potential_hits = []
        misuse_file = misuse.location.file
        misuse_method = misuse.location.method
        for finding in findings:
            if "file" in finding:
                matches_file = Evaluate.__matches_file(finding, misuse_file)
                matches_method = Evaluate.__matches_method(finding, misuse_method)
                if matches_file and matches_method:
                    logger.debug("Detector found something in '%s'.", misuse_file)
                    potential_hits.append(finding)

        return potential_hits

    @staticmethod
    def __matches_file(finding, misuse_file):
        finding_file = finding["file"]
        # If file is an inner class "Outer$Inner.class", the source file is "Outer.java".
        if "$" in finding_file:
            finding_file = finding_file.split("$", 1)[0] + ".java"
        # If file is a class file "A.class", the source file is "A.java".
        if finding_file.endswith(".class"):
            finding_file = finding_file[:-5] + "java"
        return finding_file.endswith(misuse_file)

    @staticmethod
    def __matches_method(finding, misuse_method):
        if "method" in finding:
            finding_method = finding["method"]
            if "(" not in finding_method:
                finding_method += "("
            return finding_method in misuse_method
        else:
            # If detector provides no method we match anything, to be on the safe side
            return True

    @staticmethod
    def __multiline(text: str):
        return "\n".join(wrap(text, width=80)) + "\n"
