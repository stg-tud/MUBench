import logging
from copy import deepcopy
from os import makedirs, remove
from os.path import join, exists, dirname
from shutil import copy
from typing import Dict, Iterable
from typing import List

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.requirements import JavaRequirement, DotRequirement
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark.data.run import Run
from benchmark.subprocesses.tasks.implementations.review import review_page
from benchmark.subprocesses.tasks.implementations.review.review_page import REVIEW_RECEIVER_FILE
from benchmark.utils.io import remove_tree, safe_write
from benchmark.utils.shell import Shell

REVIEW_UTILS_FILE = "review_utils.php"


def _copy_review_resource_file(resource_name: str, destination_path: str):
    copy(join(dirname(__file__), "review", resource_name), join(destination_path, resource_name))


class Review:
    def __init__(self, detector: Detector):
        self.detector = detector
        self.project_reviews = []  # type: List[ProjectReview]
        self.__current_project_review = None  # type: ProjectReview

    def start_project_review(self, project_id: str):
        self.__current_project_review = ProjectReview(project_id)
        self.project_reviews.append(self.__current_project_review)

    def start_run_review(self, name: str, run: Run):
        self.__current_project_review.start_run_review(name, run)

    def append_finding_review(self, name: str, violation_types: List[str], has_findings: bool,
                              details_url: str, details_path: str, details_prefix: str):
        self.__current_project_review.append_finding_review(name, violation_types, has_findings,
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

    def append_finding_review(self, name: str, violation_types: List[str], has_findings: bool,
                              details_url: str, details_path: str, details_prefix: str):
        self.run_reviews[len(self.run_reviews) - 1].append_finding_review(name, violation_types, has_findings,
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

    def append_finding_review(self, name: str, violation_types: List[str], has_findings: bool,
                              details_url: str, details_path: str, details_prefix: str):
        self.finding_reviews.append(FindingReview(name, violation_types, has_findings, details_url, details_path,
                                                  details_prefix))

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
    def __init__(self, name: str, violation_types: List[str], has_findings: bool, details_url: str,
                 details_path: str, details_prefix: str):
        self.name = name
        self.violation_types = violation_types
        self.has_findings = has_findings
        self.details_url = details_url
        self.details_path = details_path
        self.details_prefix = details_prefix

    def to_html(self):
        if self.has_findings:
            result = "<a href=\"{}\">review</a>".format(self.details_url)
        else:
            result = "<a href=\"{}\">no findings</a>".format(self.details_url)

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
    def __init__(self, experiment: Experiment, checkout_base_dir: str, compiles_path: str, force_prepare: bool,
                 details_page_generator):
        super().__init__()
        self.experiment = experiment
        self.detector = experiment.detector
        self.compiles_path = compiles_path
        self.detector_findings_path = self.experiment.findings_path
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
        logger = logging.getLogger("review_prepare.version")

        detector_run = self.experiment.get_run(version)
        if not detector_run.result:
            logger.info("No results on %s.", version)
        else:
            logger.info("Prepare results on %s.", version)
            self.__review.start_run_review(version.version_id, detector_run)
            super().process_project_version(project, version)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        logger = logging.getLogger("review_prepare.misuse")

        detector_run = self.experiment.get_run(version)

        if not detector_run.is_success():
            logger.info("Skipping %s in %s: no result.", misuse, version)
            self.__append_misuse_no_hits(version, misuse, "run: {}".format(detector_run.result))
            return Response.skip

        review_dir = self.experiment.get_review_dir(version, misuse)
        review_path = self.experiment.get_review_path(version, misuse)

        review_details_url = join(review_dir, "review.php")
        review_details_path = join(review_path, "review.php")
        review_no_findings_url = join(review_dir, "no_findings.php")
        review_no_findings_path = join(review_path, "no_findings.php")

        if self.force_prepare:
            logger.debug("Removing old review files for %s in %s...", misuse, version)
            remove_tree(review_path)

        if exists(review_path):
            if exists(review_details_path):
                self.__append_misuse_review(version, misuse, review_details_url)
            else:
                self.__append_misuse_no_hits(version, misuse, review_no_findings_url)

            logger.info("%s in %s is already prepared.", misuse, version)
            return Response.ok

        logger.debug("Checking hit for %s in %s...", misuse, version)

        potential_hits = detector_run.get_potential_hits(misuse)

        logger.info("Found %s potential hits for %s.", len(potential_hits), misuse)
        logger.debug("Generating review files for %s in %s...", misuse, version)

        if potential_hits:
            potential_hits = _specialize_findings(self.detector, potential_hits, review_path)
            self.details_page_generator(self.experiment.id, review_details_path, self.detector,
                                        self.compiles_path, version, misuse, potential_hits)
            self.__append_misuse_review(version, misuse, review_details_url)
        else:
            self.details_page_generator(self.experiment.id, review_no_findings_path, self.detector,
                                        self.compiles_path, version, misuse, [])
            self.__append_misuse_no_hits(version, misuse, review_no_findings_url)

        return Response.ok

    def __append_misuse_review(self, version: ProjectVersion, misuse: Misuse, review_site: str):
        self.__append_misuse_to_review(version, misuse, review_site, True)

    def __append_misuse_no_hits(self, version: ProjectVersion, misuse: Misuse, review_site: str):
        self.__append_misuse_to_review(version, misuse, review_site, False)

    def __append_misuse_to_review(self, version: ProjectVersion, misuse: Misuse, review_details_url: str,
                                  has_findings: bool):
        review_details_path = join(version.project_id, version.version_id, misuse.misuse_id)
        self.__review.append_finding_review(misuse.id, misuse.characteristics, has_findings,
                                            review_details_url, review_details_path, "review")

    def end(self):
        safe_write(self.__review.to_html(), join(self.experiment.reviews_path, self.detector.id, "index.php"), append=False)
        _copy_review_resource_file(REVIEW_RECEIVER_FILE, join(self.experiment.reviews_path, ".."))
        _copy_review_resource_file(REVIEW_UTILS_FILE, join(self.experiment.reviews_path, ".."))


class PrepareReviewOfBenchmarkWithPatternsTask(ReviewPrepare):
    def __init__(self, experiment: Experiment, checkout_base_dir: str, compiles_path: str, force_prepare: bool):
        super().__init__(experiment, checkout_base_dir, compiles_path, force_prepare,
                         review_page.generate_ex1)


class PrepareReviewOfBenchmarkTask(ReviewPrepare):
    def __init__(self, experiment: Experiment, checkout_base_dir: str, compiles_path: str, force_prepare: bool):
        super().__init__(experiment, checkout_base_dir, compiles_path, force_prepare,
                         review_page.generate_ex2)


class PrepareReviewOfTopFindingsTask(ProjectVersionTask):
    def __init__(self, experiment: Experiment, checkouts_path: str, compiles_path: str, top_n_findings: int,
                 force_prepare: bool):
        super().__init__()
        self.experiment = experiment
        self.compiles_path = compiles_path
        self.checkouts_path = checkouts_path
        self.top_n_findings = top_n_findings
        self.force_prepare = force_prepare
        self.detector = experiment.detector

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

        detector_run = self.experiment.get_run(version)
        run_dir = self.experiment.get_review_dir(version)  # TODO run or review?
        review_path = self.experiment.get_review_path(version)

        self.__review.start_run_review(version.version_id, detector_run)

        if not detector_run.is_success():
            logger.info("Skipping %s: no result.", version)
            return

        if self.force_prepare:
            logger.debug("Removing old review files for %s...", version)
            remove_tree(review_path)

        logger.info("Generating review files for %s...", version)
        findings = _sort_findings(self.detector, detector_run.findings)[:self.top_n_findings]
        logger.info("    Preparing files for %d findings...", len(findings))

        for finding in findings:
            finding_name = "finding-{}".format(finding["id"])
            details_url = join(run_dir, finding_name + ".php")
            details_path = join(review_path, finding_name + ".php")

            if self.force_prepare and exists(details_path):
                remove(details_path)

            if exists(details_path):
                logger.debug("    %s in %s is already prepared.", finding_name, version)
            else:
                logger.debug("    Generating review file for %s in %s...", finding_name, version)
                review_page.generate_ex3(self.experiment.id, details_path, self.detector.id, self.compiles_path,
                                         version,
                                         _specialize_finding(finding, self.detector, dirname(details_path)))

            self.__review.append_finding_review("Finding {}".format(finding["id"]), ["<i>unknown</i>"],
                                                True, details_url, run_dir, finding_name)

    def end(self):
        safe_write(self.__review.to_html(), join(self.experiment.reviews_path, self.detector.id, "index.php"), append=False)
        _copy_review_resource_file(REVIEW_RECEIVER_FILE, join(self.experiment.reviews_path, ".."))
        _copy_review_resource_file(REVIEW_UTILS_FILE, join(self.experiment.reviews_path, ".."))


# TODO move this to detector-specific review-page generators
def _specialize_findings(detector: Detector, findings: List[Dict[str, str]], base_path):
    findings = _sort_findings(detector, findings)
    for finding in findings:
        _specialize_finding(finding, detector, base_path)
    return findings


def _specialize_finding(finding, detector: Detector, base_path: str):
    if detector.id == "dmmc":
        __format_float_value(finding, "strangeness")
    elif detector.id == "jadet" or detector.id == "tikanga":
        __format_float_value(finding, "confidence")
        __format_float_value(finding, "defect_indicator")
    elif detector.id == "grouminer":
        __format_float_value(finding, "rareness")
        __replace_dot_graph_with_image(finding, "overlap", base_path)
        __replace_dot_graph_with_image(finding, "pattern", base_path)
    elif detector.id == "mudetect":
        __replace_dot_graph_with_image(finding, "pattern_violation", base_path)
    return finding


def _sort_findings(detector: Detector, findings: List[Dict[str, str]]):
    if detector.id == "dmmc":
        sort_by = "strangeness"
    elif detector.id == "jadet" or detector.id == "tikanga":
        sort_by = "defect_indicator"
    elif detector.id == "grouminer":
        sort_by = "rareness"
    elif detector.id == "mudetect":
        sort_by = "confidence"
    else:
        sort_by = None

    findings = deepcopy(findings)
    if sort_by:
        findings.sort(key=lambda f: float(f[sort_by]), reverse=True)
    return findings


def __format_float_value(finding, float_key):
    finding[float_key] = str(round(float(finding[float_key]), 3))


def __replace_dot_graph_with_image(finding, key, base_path):
    image_name = "f{}-{}.png".format(finding["id"], key)
    __create_image(finding[key], join(base_path, image_name))
    finding[key] = """<img src="./{}" />""".format(image_name)


def __create_image(dot_graph, file):
    makedirs(dirname(file), exist_ok=True)
    Shell.exec("""echo "{}" | dot -Tpng -o"{}" """.format(dot_graph.replace("\\", "\\\\").replace("\"", "\\\""), file))
