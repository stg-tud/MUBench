import logging
from copy import deepcopy
from os import makedirs, remove
from os.path import join, exists, dirname
from shutil import copy
from typing import Dict, Iterable, Optional
from typing import List

import yaml

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.requirements import JavaRequirement, DotRequirement
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark.subprocesses.tasks.implementations.detect import Run
from benchmark.subprocesses.tasks.implementations.review import review_page
from benchmark.subprocesses.tasks.implementations.review.review_page import REVIEW_RECEIVER_FILE
from benchmark.utils.io import safe_open, remove_tree, safe_write
from benchmark.utils.shell import Shell

REVIEW_UTILS_FILE = "review_utils.php"


def _copy_review_resource_file(resource_name: str, destination_path: str):
    copy(join(dirname(__file__), "review", resource_name), join(destination_path, resource_name))


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

    def append_finding_review(self, name: str, violation_types: List[str],
                              details_url: str, details_path: str, details_prefix: str):
        self.__current_project_review.append_finding_review(name, violation_types,
                                                            details_url, details_path, details_prefix)

    def to_html(self):
        review = """<?php include "../../{}"; ?>
                <h1>Detector: {}</h1>
            """.format(REVIEW_UTILS_FILE, self.detector)
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

    def append_finding_review(self, name: str, violation_types: List[str],
                              details_url: str, details_path: str, details_prefix: str):
        self.run_reviews[len(self.run_reviews) - 1].append_finding_review(name, violation_types,
                                                                          details_url, details_path, details_prefix)

    def to_html(self):
        if self.run_reviews:
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
        else:
            return ""


class RunReview:
    def __init__(self, name: str, run: Run):
        self.version_id = name
        self.run = run
        self.finding_reviews = []

    def append_finding_review(self, name: str, violation_types: List[str],
                              details_url: str, details_path: str, details_prefix: str):
        self.finding_reviews.append(FindingReview(name, violation_types, details_url, details_path, details_prefix))

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
                        <tr><th>Misuse</th><th>Violation Types</th><th>Result</th><th>Reviewed By</th></tr>"""
            for misuse_review in self.finding_reviews:
                review += misuse_review.to_html()
            review += """
                    </table>
                </td>
            </tr>
            """
        return review


class FindingReview:
    def __init__(self, name: str, violation_types: List[str], details_url: str, details_path: str, details_prefix: str):
        self.name = name
        self.violation_types = violation_types
        self.details_url = details_url
        self.details_path = details_path
        self.details_prefix = details_prefix

    def to_html(self):
        if self.details_url:
            result = "<a href=\"{}\">review</a>".format(self.details_url)
        else:
            result = "no findings"

        reviewed_by = """<?php echo join(", ", get_reviewer_links("{}", "{}", "{}")); ?>""".format(self.details_url,
                                                                                                   self.details_path,
                                                                                                   self.details_prefix)

        return """
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>
            """.format(self.name, "<br/>".join(self.violation_types), result, reviewed_by)


class ReviewPrepare(ProjectVersionMisuseTask):
    no_hit = 0
    potential_hit = 1

    def __init__(self, experiment: str, detector: str, findings_path: str, reviews_path: str, checkout_base_dir: str,
                 compiles_path: str, force_prepare: bool, details_page_generator):
        super().__init__()
        self.experiment = experiment
        self.detector = detector
        self.compiles_path = compiles_path
        self.findings_path = findings_path
        self.reviews_path = reviews_path
        self.review_path = join(reviews_path, experiment, detector)
        self.checkout_base_dir = checkout_base_dir
        self.force_prepare = force_prepare
        self.details_page_generator = details_page_generator

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
        if detector_run.result:
            self.__review.start_run_review(version.version_id, detector_run)
            super().process_project_version(project, version)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        logger = logging.getLogger("review_prepare.misuse")

        findings_path = join(self.findings_path, project.id, version.version_id)
        detector_run = Run(findings_path)

        if not detector_run.is_success():
            logger.info("Skipping %s in %s: no result.", misuse, version)
            self.__append_misuse_to_review(version, misuse, "run: {}".format(detector_run.result))
            return Response.skip

        review_dir = join(project.id, version.version_id, misuse.id)
        review_site = join(review_dir, "review.php")
        review_path = join(self.review_path, review_dir)

        if self.force_prepare:
            logger.debug("Removing old review files for %s in %s...", misuse, version)
            remove_tree(review_path)

        if exists(review_path):
            if exists(join(self.review_path, review_site)):
                self.__append_misuse_review(version, misuse, review_site)
            else:
                self.__append_misuse_no_hits(version, misuse)

            logger.info("%s in %s is already prepared.", misuse, version)
            return Response.ok

        logger.debug("Checking hit for %s in %s...", misuse, version)

        findings = detector_run.findings
        potential_hits = ReviewPrepare.find_potential_hits(findings, misuse)
        logger.info("Found %s potential hits for %s.", len(potential_hits), misuse)
        logger.debug("Generating review files for %s in %s...", misuse, version)

        if potential_hits:
            potential_hits = _specialize_findings(self.detector, potential_hits, review_path)
            self.details_page_generator(self.experiment, join(self.review_path, review_site), self.detector,
                                        self.compiles_path, version, misuse, potential_hits)
            self.__generate_potential_hits_yaml(potential_hits, review_path)
            self.__append_misuse_review(version, misuse, review_site)
        else:
            makedirs(review_path)
            self.__append_misuse_no_hits(version, misuse)

        return Response.ok

    def __append_misuse_review(self, version: ProjectVersion, misuse: Misuse, review_site: str):
        self.__append_misuse_to_review(version, misuse, review_site)

    def __append_misuse_no_hits(self, version: ProjectVersion, misuse: Misuse):
        self.__append_misuse_to_review(version, misuse, None)

    def __append_misuse_to_review(self, version: ProjectVersion, misuse: Misuse, review_details_url: Optional[str]):
        review_details_path = join(version.project_id, version.version_id, misuse.id)
        self.__review.append_finding_review(misuse.id, misuse.characteristics,
                                            review_details_url, review_details_path, "review")

    @staticmethod
    def __generate_potential_hits_yaml(potential_hits: List[Dict[str, str]], review_path: str):
        with safe_open(join(review_path, 'potentialhits.yml'), 'w+') as file:
            yaml.dump_all(potential_hits, file)

    def end(self):
        safe_write(self.__review.to_html(), join(self.review_path, "index.php"), append=False)
        _copy_review_resource_file(REVIEW_RECEIVER_FILE, self.reviews_path)
        _copy_review_resource_file(REVIEW_UTILS_FILE, self.reviews_path)

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


class ReviewPrepareEx1(ReviewPrepare):
    def __init__(self, experiment: str, detector: str, findings_path: str, reviews_path: str, checkout_base_dir: str,
                 compiles_path: str, force_prepare: bool):
        super().__init__(experiment, detector, findings_path, reviews_path, checkout_base_dir, compiles_path,
                         force_prepare, review_page.generate_ex1)


class ReviewPrepareEx2(ReviewPrepare):
    def __init__(self, experiment: str, detector: str, findings_path: str, reviews_path: str, checkout_base_dir: str,
                 compiles_path: str, force_prepare: bool):
        super().__init__(experiment, detector, findings_path, reviews_path, checkout_base_dir, compiles_path,
                         force_prepare, review_page.generate_ex2)


class ReviewPrepareEx3(ProjectVersionTask):
    def __init__(self, experiment: str, detector: str, findings_path: str, reviews_path: str, checkouts_path: str,
                 compiles_path: str, force_prepare: bool):
        super().__init__()
        self.experiment = experiment
        self.compiles_path = compiles_path
        self.findings_path = findings_path
        self.reviews_path = reviews_path
        self.review_path = join(reviews_path, experiment, detector)
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
        logger = logging.getLogger("review_prepare.version")

        run_dir = join(project.id, version.version_id)
        findings_path = join(self.findings_path, run_dir)
        detector_run = Run(findings_path)
        self.__review.start_run_review(version.version_id, detector_run)

        if not detector_run.is_success():
            logger.info("Skipping %s: no result.", version)
            return

        if self.force_prepare:
            logger.debug("Removing old review files for %s...", version)
            remove_tree(join(self.review_path, project.id, version.version_id))

        logger.info("Generating review files for %s...", version)
        findings = _sort_findings(self.detector, detector_run.findings)
        logger.info("    Preparing files for %d findings...", len(findings))

        for finding in findings:
            finding_name = "finding-{}".format(finding["id"])
            details_url = join(project.id, version.version_id, finding_name + ".php")
            details_path = join(self.review_path, details_url)

            if self.force_prepare:
                remove(details_path)

            if exists(details_path):
                logger.debug("    %s in %s is already prepared.", finding_name, version)
            else:
                logger.debug("    Generating review file for %s in %s...", finding_name, version)
                review_page.generate_ex3(self.experiment, details_path, self.detector, self.compiles_path, version,
                                         _specialize_finding(finding, self.detector, dirname(details_path)))

            self.__review.append_finding_review("Finding {}".format(finding["id"]), ["<i>unknown</i>"],
                                                details_url, run_dir, finding_name)

    def end(self):
        safe_write(self.__review.to_html(), join(self.review_path, "index.php"), append=False)
        _copy_review_resource_file(REVIEW_RECEIVER_FILE, self.reviews_path)
        _copy_review_resource_file(REVIEW_UTILS_FILE, self.reviews_path)


# TODO move this to detector-specific review-page generators
def _specialize_findings(detector: str, findings: List[Dict[str, str]], base_path):
    findings = _sort_findings(detector, findings)
    for finding in findings:
        _specialize_finding(finding, detector, base_path)
    return findings


def _specialize_finding(finding, detector, base_path):
    if detector.startswith("dmmc"):
        __format_float_value(finding, "strangeness")
    elif detector.startswith("jadet") or detector.startswith("tikanga"):
        __format_float_value(finding, "confidence")
        __format_float_value(finding, "defect_indicator")
    elif detector.startswith("grouminer"):
        __format_float_value(finding, "rareness")
        __replace_dot_graph_with_image(finding, "overlap", base_path)
        __replace_dot_graph_with_image(finding, "pattern", base_path)
    elif detector.startswith("mudetect"):
        finding["overlap"] = finding["overlap"].replace(":0:0", "")
        __replace_dot_graph_with_image(finding, "overlap", base_path)
        finding["pattern"] = finding["pattern"].replace(":0:0", "")
        __replace_dot_graph_with_image(finding, "pattern", base_path)
    return finding


def _sort_findings(detector: str, findings: List[Dict[str, str]]):
    findings = deepcopy(findings)
    if detector.startswith("dmmc"):
        findings.sort(key=lambda f: float(f["strangeness"]), reverse=True)
    elif detector.startswith("jadet") or detector.startswith("tikanga"):
        findings.sort(key=lambda f: float(f["defect_indicator"]))
    elif detector.startswith("grouminer"):
        findings.sort(key=lambda f: float(f["rareness"]), reverse=True)
    return findings


def __format_float_value(finding, float_key):
    finding[float_key] = str(round(float(finding[float_key]), 3))


def __replace_dot_graph_with_image(finding, key, base_path):
    image_name = "f{}-{}.png".format(finding["id"], key)
    __create_image(finding[key], join(base_path, image_name))
    finding[key] = """<img src="./{}" />""".format(image_name)


def __create_image(dot_graph, file):
    makedirs(dirname(file), exist_ok=True)
    Shell.exec("""echo "{}" | dot -Tpng -o"{}" """.format(dot_graph.replace("\"", "\\\""), file))
