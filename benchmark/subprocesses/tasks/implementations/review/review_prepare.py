import logging
from os.path import join, exists, pardir, basename
from typing import Dict, Iterable
from typing import List

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.subprocesses.tasks.implementations.detect import Run
from benchmark.subprocesses.tasks.implementations.review.html_generators import main_index, detector_index, \
    project_index, version_index, review_page
from benchmark.utils.io import safe_open, remove_tree


class ReviewPrepare(ProjectVersionMisuseTask):
    no_hit = 0
    potential_hit = 1

    def __init__(self, results_path: str, review_path: str, checkout_base_dir: str, eval_result_file: str,
                 force_prepare: bool):
        super().__init__()
        self.results_path = results_path
        self.review_path = review_path
        self.checkout_base_dir = checkout_base_dir
        self.eval_result_file = eval_result_file
        self.force_prepare = force_prepare

        self.detector = basename(self.results_path)

        self.results = []

    def start(self):
        detector_index.generate(self.review_path, self.results_path)

    def new_project(self, project: Project):
        if exists(join(self.results_path, project.id)):
            project_index.generate(join(self.review_path, project.id), join(self.results_path, project.id), project)

    def new_version(self, project: Project, version: ProjectVersion):
        if exists(join(self.results_path, project.id, version.version_id)):
            version_index.generate(join(self.review_path, project.id, version.version_id),
                                   join(self.results_path, project.id, version.version_id), project, version)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        logger = logging.getLogger("review_prepare")

        review_folder = join(self.review_path, project.id, version.version_id, misuse.id)
        if exists(review_folder) and not self.force_prepare:
            logger.info("%s in %s is already prepared.", misuse, version)
            return Response.ok

        findings_path = join(self.results_path, project.id, version.version_id)
        detector_run = Run(findings_path)

        if not detector_run.is_success():
            logger.info("Skipping %s in %s: no result.", misuse, version)
            return Response.skip

        logger.debug("Checking hit for %s in %s...", misuse, version)

        findings = detector_run.findings
        potential_hits = ReviewPrepare.__find_potential_hits(findings, misuse)

        logger.info("Found %s potential hits for %s.", len(potential_hits), misuse)
        self.results.append((misuse.id, len(potential_hits)))

        remove_tree(review_folder)
        logger.debug("Generating review files for %s in %s...", misuse, version)

        review_page.generate(review_folder, findings_path, self.detector, project, version, misuse, potential_hits)

        return Response.ok

    def end(self):
        main_review_dir = join(self.review_path, pardir)
        main_findings_dir = join(self.results_path, pardir)
        if exists(main_findings_dir):
            main_index.generate(main_review_dir, main_findings_dir)

        with safe_open(join(self.results_path, self.eval_result_file), 'w+') as file_result:
            for result in self.results:
                print(str(result).lstrip('(').rstrip(')'), file=file_result)

    @staticmethod
    def __find_potential_hits(findings: Iterable[Dict[str, str]], misuse: Misuse) -> List[Dict[str, str]]:
        candidates = ReviewPrepare.__filter_by_file(findings, misuse.location.file)
        return ReviewPrepare.__filter_by_method(candidates, misuse.location.method)

    @staticmethod
    def __filter_by_file(findings, misuse_file):
        matches = []
        for finding in findings:
            if ReviewPrepare.__matches_file(finding["file"], misuse_file):
                matches.append(finding)
        return matches

    @staticmethod
    def __matches_file(finding_file, misuse_file):
        # If file is an inner class "Outer$Inner.class", the source file is "Outer.java".
        if "$" in finding_file:
            finding_file = finding_file.split("$", 1)[0] + ".java"
        # If file is a class file "A.class", the source file is "A.java".
        if finding_file.endswith(".class"):
            finding_file = finding_file[:-5] + "java"
        return finding_file.endswith(misuse_file)

    @staticmethod
    def __filter_by_method(findings, misuse_method):
        matches = []

        for finding in findings:
            method = finding.get("method", None)

            # don't filter if the detector did not have a method output
            if not method:
                matches.append(finding)
                continue

            # if detector reports only method names, this ensures we don't match prefixes of method names
            if "(" not in method:
                method += "("
            if method in misuse_method:
                matches.append(finding)

        if not matches:
            # fall back to match without the signature
            for finding in findings:
                method = finding["method"].split("(")[0] + "("
                if method in misuse_method:
                    matches.append(finding)

        return matches
