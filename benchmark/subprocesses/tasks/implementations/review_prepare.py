import logging
import yaml
from os import makedirs, listdir
from os.path import join, exists, pardir, basename
from typing import Dict, Iterable
from typing import List

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.subprocesses.tasks.implementations.detect import Run
from benchmark.subprocesses.tasks.implementations.review import main_index, review_page
from benchmark.utils.io import safe_open, remove_tree, safe_write, read_yaml


class ReviewPrepare(ProjectVersionMisuseTask):
    no_hit = 0
    potential_hit = 1

    def __init__(self, results_path: str, review_path: str, checkout_base_dir: str, compiles_path: str,
                 eval_result_file: str, force_prepare: bool):
        super().__init__()
        self.compiles_path = compiles_path
        self.results_path = results_path
        self.review_path = review_path
        self.checkout_base_dir = checkout_base_dir
        self.eval_result_file = eval_result_file
        self.force_prepare = force_prepare

        self.detector = basename(self.results_path)

        self.results = []

        self.projects_to_review = []
        self.versions_to_review = []
        self.misuses_to_review = []

    def start(self):
        logger = logging.getLogger("review_prepare")
        logger.info("Preparing review for results of %s...", self.detector)

    def process_project(self, project: Project):
        self.versions_to_review.clear()

        super().process_project(project)

        project_to_review = "<h2>Project: {}</h2>\n<table>\n".format(project.id)
        for version_to_review in self.versions_to_review:
            project_to_review += version_to_review
        project_to_review += "</table>\n"

        self.projects_to_review.append(project_to_review)

    def process_project_version(self, project: Project, version: ProjectVersion):
        self.misuses_to_review.clear()

        super().process_project_version(project, version)

        findings_path = join(self.results_path, project.id, version.version_id)
        detector_run = Run(findings_path)

        version_to_review = "<tr><td>Version:</td><td>{} ({} findings in total)</td></tr>\n" \
                            "<tr><td></td><td><table>\n".format(version.version_id, len(detector_run.findings))
        for misuse_to_review in self.misuses_to_review:
            version_to_review += misuse_to_review
        version_to_review += "</table></td></tr>\n"

        self.versions_to_review.append(version_to_review)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        logger = logging.getLogger("review_prepare.misuse")

        findings_path = join(self.results_path, project.id, version.version_id)
        detector_run = Run(findings_path)

        if not detector_run.is_success():
            logger.info("Skipping %s in %s: no result.", misuse, version)
            self.__append_misuse_to_review(misuse, "run: {}".format(detector_run.result), [])
            return Response.skip

        review_dir = join(project.id, version.version_id, misuse.id)
        review_site = join(review_dir, "review.html")
        review_path = join(self.review_path, review_dir)
        if exists(review_path) and not self.force_prepare:
            if exists(join(self.review_path, review_site)):
                existing_reviews = self.__get_existing_reviews(review_path)
                self.__append_misuse_review(misuse, review_site, existing_reviews)
            else:
                self.__append_misuse_no_hits(misuse)

            logger.info("%s in %s is already prepared.", misuse, version)
            return Response.ok

        logger.debug("Checking hit for %s in %s...", misuse, version)

        findings = detector_run.findings
        potential_hits = ReviewPrepare.__find_potential_hits(findings, misuse)

        logger.info("Found %s potential hits for %s.", len(potential_hits), misuse)
        self.results.append((misuse.id, len(potential_hits)))

        remove_tree(review_path)
        logger.debug("Generating review files for %s in %s...", misuse, version)

        if potential_hits:
            review_page.generate(review_path, self.detector, self.compiles_path, project, version, misuse,
                                 potential_hits)
            self.__generate_potential_hits_yaml(potential_hits, review_path)
            self.__append_misuse_review(misuse, review_site, [])
        else:
            makedirs(review_path)
            self.__append_misuse_no_hits(misuse)

        return Response.ok

    def __append_misuse_review(self, misuse: Misuse, review_site: str, existing_reviews: List[Dict[str, str]]):
        self.__append_misuse_to_review(misuse, "<a href=\"{}\">review</a>".format(review_site), existing_reviews)

    def __append_misuse_no_hits(self, misuse: Misuse):
        self.__append_misuse_to_review(misuse, "no potential hits", [])

    def __append_misuse_to_review(self, misuse: Misuse, result: str, existing_reviews: List[Dict[str, str]]):
        reviewers = [review['reviewer'] for review in existing_reviews if review.get('reviewer', None) is not None]
        reviewed_by = 'reviewed by ' + ', '.join(reviewers) if reviewers else ''

        misuse_to_review = "<tr><td>Misuse:</td><td>{}</td>\n<td>[{}] {}</td></tr>\n".format(misuse.misuse_id, result,
                                                                                             reviewed_by)
        self.misuses_to_review.append(misuse_to_review)

    @staticmethod
    def __get_existing_reviews(review_path: str) -> List[Dict[str, str]]:
        existing_review_files = [join(review_path, file) for file in listdir(review_path) if
                                 file.startswith('review') and file.endswith('.yml')]
        existing_reviews = []
        for existing_review_file in existing_review_files:
            existing_reviews.append(read_yaml(existing_review_file))
        return existing_reviews

    @staticmethod
    def __generate_potential_hits_yaml(potential_hits: List[Dict[str, str]], review_path: str):
        with safe_open(join(review_path, 'potentialhits.yml'), 'w+') as file:
            yaml.dump_all(potential_hits, file)

    def end(self):
        detector_to_review = "<h1>Detector: {}</h1>\n".format(self.detector)
        for project_to_review in self.projects_to_review:
            detector_to_review += project_to_review
        safe_write(detector_to_review, join(self.review_path, "index.html"), append=False)

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
        candidates = ReviewPrepare.__filter_by_method(candidates, misuse.location.method)
        return candidates

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
            if "method" in finding:
                method = finding["method"]
                # if detector reports only method names, this ensures we don't match prefixes of method names
                if "(" not in method:
                    method += "("
                if method in misuse_method:
                    matches.append(finding)
            else:
                # don't filter if the detector reports no method
                matches.append(finding)

        if not matches:
            # fall back to match without the signature
            for finding in findings:
                method = finding["method"].split("(")[0] + "("
                if method in misuse_method:
                    matches.append(finding)

        return matches
