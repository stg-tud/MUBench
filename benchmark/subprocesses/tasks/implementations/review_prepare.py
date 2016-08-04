import logging
from copy import deepcopy
from os import makedirs, listdir
from os.path import join, exists, dirname
from shutil import copy
from typing import Dict, Iterable
from typing import List

import yaml

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.requirements import JavaRequirement, DotRequirement
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark.subprocesses.tasks.implementations.detect import Run, Result
from benchmark.subprocesses.tasks.implementations.review import review_page
from benchmark.utils.io import safe_open, remove_tree, safe_write, read_yaml
from benchmark.utils.shell import Shell


class Review:
    def __init__(self, detector: str):
        self.detector = detector
        self.project_reviews = []  # type: List[ProjectReview]
        self.__current_project_review = None  # type: ProjectReview

    def start_project_review(self, project_id: str):
        self.__current_project_review = ProjectReview(project_id)
        self.project_reviews.append(self.__current_project_review)

    def start_run_review(self, name: str, run: Run):
        self.__current_project_review.start_run_review(name, run)

    def append_finding_review(self, name: str, result: str, reviewers: List[str]):
        self.__current_project_review.append_finding_review(name, result, reviewers)

    def to_html(self):
        review = "<h1>Detector: {}</h1>".format(self.detector)
        for project_review in self.project_reviews:
            review += project_review.to_html()
        return review


class ProjectReview:
    def __init__(self, project_id):
        self.project_id = project_id
        self.run_reviews = []  # type: List[RunReview]
        self.__current_run_review = None  # type: RunReview

    def start_run_review(self, name: str, run: Run):
        self.run_reviews.append(RunReview(name, run))

    def append_finding_review(self, name: str, result: str, reviewers: List[str]):
        self.run_reviews[len(self.run_reviews) - 1].append_finding_review(name, result, reviewers)

    def to_html(self):
        review = """
            <h2>Project: {}</h2>
            <table>
            """.format(self.project_id)
        for version_review in self.run_reviews:
            review += version_review.to_html()
        review += """
            </table>
            """
        return review


class RunReview:
    def __init__(self, name: str, run: Run):
        self.version_id = name
        self.run = run
        self.finding_reviews = []

    def append_finding_review(self, name: str, result: str, reviewers: List[str]):
        self.finding_reviews.append(FindingReview(name, result, reviewers))

    def to_html(self):
        result_name = self.run.result.name if self.run.result else "not run"
        if self.run.is_failure():
            result_name = """<b style="color:red">{}</b>""".format(result_name)

        review = """
            <tr>
                <td>Version:</td>
                <td>{} (result: {}, findings: {}, runtime: {}s)</td>
            </tr>
            """.format(self.version_id,
                       result_name,
                       len(self.run.findings) if self.run.result else "none",
                       round(self.run.runtime, 1) if self.run.result else "unknown")
        if self.finding_reviews:
            review += """
            <tr>
                <td></td>
                <td>
                    <table border=\"1\" cellpadding=\"5\">
                        <tr><th>Misuse</th><th>Result</th><th>Reviewed By</th></tr>"""
            for misuse_review in self.finding_reviews:
                review += misuse_review.to_html()
            review += """
                    </table>
                </td>
            </tr>
            """
        return review


class FindingReview:
    def __init__(self, name: str, result: str, reviewers: List[str]):
        self.name = name
        self.result = result
        self.reviewers = reviewers

    def to_html(self):
        reviewed_by = ", ".join(self.reviewers) if self.reviewers else "not reviewed"
        return """
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>
            """.format(self.name, self.result, reviewed_by)


class ReviewPrepare(ProjectVersionMisuseTask):
    no_hit = 0
    potential_hit = 1

    def __init__(self, detector: str, findings_path: str, review_path: str, checkout_base_dir: str, compiles_path: str,
                 force_prepare: bool):
        super().__init__()
        self.compiles_path = compiles_path
        self.findings_path = findings_path
        self.review_path = review_path
        self.checkout_base_dir = checkout_base_dir
        self.force_prepare = force_prepare
        self.detector = detector

        self.__review = Review(self.detector)

    def get_requirements(self):
        return [JavaRequirement()]

    def start(self):
        logger = logging.getLogger("review_prepare")
        logger.info("Preparing review for results of %s...", self.detector)

    def process_project(self, project: Project):
        self.__review.start_project_review(project.id)
        super().process_project(project)

    def process_project_version(self, project: Project, version: ProjectVersion):
        findings_path = join(self.findings_path, project.id, version.version_id)
        detector_run = Run(findings_path)
        self.__review.start_run_review(version.version_id, detector_run)
        if detector_run.is_success():
            super().process_project_version(project, version)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        logger = logging.getLogger("review_prepare.misuse")

        findings_path = join(self.findings_path, project.id, version.version_id)
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
        potential_hits = ReviewPrepare.find_potential_hits(findings, misuse)
        logger.info("Found %s potential hits for %s.", len(potential_hits), misuse)
        remove_tree(review_path)
        logger.debug("Generating review files for %s in %s...", misuse, version)

        if potential_hits:
            review_page.generate(review_path, self.detector, self.compiles_path, project, version, misuse,
                                 _specialize_findings(self.detector, potential_hits, review_path))
            self.__generate_potential_hits_yaml(potential_hits, review_path)
            self.__append_misuse_review(misuse, review_site, [])
        else:
            makedirs(review_path)
            self.__append_misuse_no_hits(misuse)

        return Response.ok

    def __append_misuse_review(self, misuse: Misuse, review_site: str, existing_reviews: List[Dict[str, str]]):
        review_potential_hits = "<a href=\"{}\">potential hits</a>".format(review_site)
        self.__append_misuse_to_review(misuse, review_potential_hits, existing_reviews)

    def __append_misuse_no_hits(self, misuse: Misuse):
        self.__append_misuse_to_review(misuse, "no potential hits", [])

    def __append_misuse_to_review(self, misuse: Misuse, result: str, existing_reviews: List[Dict[str, str]]):
        reviewers = [review['reviewer'] for review in existing_reviews if review.get('reviewer', None)]
        self.__review.append_finding_review(misuse.id, result, reviewers)

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
        safe_write(self.__review.to_html(), join(self.review_path, "index.html"), append=False)

    @staticmethod
    def find_potential_hits(findings: Iterable[Dict[str, str]], misuse: Misuse) -> List[Dict[str, str]]:
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


class ReviewPrepareAll(ProjectVersionTask):
    def __init__(self, detector: str, findings_path: str, review_path: str, checkouts_path: str, compiles_path: str,
                 force_prepare: bool):
        super().__init__()
        self.compiles_path = compiles_path
        self.findings_path = findings_path
        self.review_path = review_path
        self.checkouts_path = checkouts_path
        self.force_prepare = force_prepare
        self.detector = detector

        self.__review = Review(self.detector)

    def get_requirements(self):
        return [JavaRequirement(), DotRequirement()]

    def start(self):
        logger = logging.getLogger("review_prepare")
        logger.info("Preparing review of all findings of %s...", self.detector)

    def process_project(self, project: Project):
        self.__review.start_project_review(project.id)
        super().process_project(project)

    def process_project_version(self, project: Project, version: ProjectVersion):
        findings_path = join(self.findings_path, project.id, version.version_id)
        detector_run = Run(findings_path)
        self.__review.start_run_review(version.version_id, detector_run)

        if not detector_run.is_success():
            return

        if self.detector.startswith("jadet") or self.detector.startswith("tikanga"):
            url = join(project.id, version.version_id, "violations.xml")
            makedirs(dirname(join(self.review_path, url)), exist_ok=True)
            copy(join(self.findings_path, url), join(self.review_path, url))
            self.__review.append_finding_review("all findings",
                                                "<a href=\"{}\">violations.xml</a>".format(url), [])
        else:
            findings = _specialize_findings(self.detector, detector_run.findings, join(self.review_path, project.id, version.version_id))

            if self.detector.startswith("dmmc"):
                findings.sort(key=lambda f: float(f["strangeness"]), reverse=True)
            elif self.detector.startswith("grouminer"):
                findings.sort(key=lambda f: float(f["rareness"]), reverse=True)

            for finding in findings:
                url = join(project.id, version.version_id, "finding-{}.html".format(finding["id"]))
                review_page.generate2(join(self.review_path, url), self.detector, self.compiles_path, version, finding)
                self.__review.append_finding_review("Finding {}".format(finding["id"]),
                                                    "<a href=\"{}\">review</a>".format(url), [])

    def end(self):
        safe_write(self.__review.to_html(), join(self.review_path, "index.html"), append=False)


# TODO move this to detector-specific review-page generators
def _specialize_findings(detector: str, findings: List[Dict[str,str]], base_path) -> List[Dict[str,str]]:
    findings = deepcopy(findings)
    if detector.startswith("grouminer"):
        for finding in findings:
            __replace_dot_graph_with_image(finding, "overlap", base_path)
            __replace_dot_graph_with_image(finding, "pattern", base_path)
    elif detector.startswith("mudetect"):
        for finding in findings:
            __replace_dot_graph_with_image(finding, "overlap", base_path)
            __replace_dot_graph_with_image(finding, "pattern", base_path)
    return findings


def __replace_dot_graph_with_image(finding, key, base_path):
    image_name = "f{}-{}.png".format(finding["id"], key)
    __create_image(finding[key], join(base_path, image_name))
    finding[key] = """<img src="./{}" />""".format(image_name)


def __create_image(dot_graph, file):
    makedirs(dirname(file), exist_ok=True)
    Shell.exec("""echo "{}" | dot -Tpng -o"{}" """.format(dot_graph.replace("\"", "\\\""), file))
