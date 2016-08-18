import logging
from os import listdir
from os.path import join, exists, basename
from typing import List, Dict
from typing import Set

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark.utils.io import read_yaml, safe_write


class FindingReview:
    def __init__(self, finding_id: int, reviewer: str, comment: str, assessment: str, violations: Set[str]):
        self.finding_id = finding_id
        self.reviewer = reviewer
        self.comment = comment
        self.assessment = assessment
        self.violations = violations


class Review:
    def __init__(self, review_file: str):
        if review_file:
            data = read_yaml(review_file)
            self.reviewer = data["reviewer"]
            self.comment = data.get("comment", "")
            self.findings = []  # type: List[FindingReview]

            if "hits" in data:
                for hit in data["hits"]:
                    review = FindingReview(hit["id"], self.reviewer, self.comment, "Yes", hit.get("vts", []))
                    self.findings.append(review)
            else:
                for finding in data["findings"]:
                    violations = finding["violations"] if "violations" in finding else []
                    review = FindingReview(finding["id"], self.reviewer, self.comment, finding["assessment"],
                                           violations)
                    self.findings.append(review)

            if not self.findings:
                file_name = basename(review_file)
                if file_name.startswith("finding-"):
                    finding_id = int(file_name.split("_")[0][8:])
                    self.findings.append(FindingReview(finding_id, self.reviewer, self.comment, "No", set()))


class ReviewCheck(ProjectVersionMisuseTask):
    def __init__(self, experiment: str, review_path: str, detectors: List[str]):
        super().__init__()
        self.experiment = experiment
        self.review_path = join(review_path, experiment)
        self.detectors = detectors
        self.output = []  # type: List[List[str]]

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        for detector in self.detectors:
            self.process_detector_project_version_misuse(detector, project, version, misuse)
        return Response.ok

    def process_detector_project_version_misuse(self, detector: str, project: Project, version: ProjectVersion,
                                                misuse: Misuse):
        review_path = join(self.review_path, detector, project.id, version.version_id, misuse.id)
        self.output += _generate_output(review_path, detector, project.id, version.version_id, misuse.id,
                                        self.__get_reviews)

    @staticmethod
    def __get_reviews(review_path: str) -> List[Review]:
        return [Review(join(review_path, file)) for file in listdir(review_path) if
                file.startswith('review_') and file.endswith('.yml')]

    def end(self):
        _write_tsv(join(self.review_path, self.experiment + "-summary.csv"), self.output)


class ReviewCheckEx3(ProjectVersionTask):
    def __init__(self, experiment: str, review_path: str, detectors: List[str]):
        super().__init__()
        self.experiment = experiment
        self.review_path = join(review_path, experiment)
        self.detectors = detectors
        self.output = []  # type: List[List[str]]

    def process_project_version(self, project: Project, version: ProjectVersion):
        for detector in self.detectors:
            self.process_detector_project_version(detector, project, version)
        return Response.ok

    def process_detector_project_version(self, detector: str, project: Project, version: ProjectVersion):
        review_path = join(self.review_path, detector, project.id, version.version_id)
        self.output += _generate_output(review_path, detector, project.id, version.version_id, "", self.__get_reviews)

    @staticmethod
    def __get_reviews(review_path: str) -> List[Review]:
        return [Review(join(review_path, file)) for file in listdir(review_path) if
                file.startswith('finding-') and file.endswith('.yml')]

    def end(self):
        _write_tsv(join(self.review_path, self.experiment + "-summary.csv"), self.output)


def _generate_output(review_path: str, detector: str, project_id: str, version_id: str, misuse_id: str, get_reviews):
    logger = logging.getLogger("review.check")
    output = []  # type: List[List[str]]

    if not exists(review_path) or not listdir(review_path):
        logger.info("No results for %s on %s version %s.", detector, project_id, version_id)
    else:
        reviews = get_reviews(review_path)
        logger.info("Adding output for %s on %s version %s (%s reviews)", detector, project_id, version_id, len(reviews))

        if not reviews:
            output.append([detector, project_id, version_id, misuse_id])

        finding_reviews_by_id = {}  # type: Dict[int,List[FindingReview]]
        for review in reviews:
            if review.findings:
                for finding_review in review.findings:
                    if finding_review.finding_id not in finding_reviews_by_id:
                        finding_reviews_by_id[finding_review.finding_id] = []
                    finding_reviews_by_id[finding_review.finding_id].append(finding_review)
            else:
                if -1 not in finding_reviews_by_id:
                    finding_reviews_by_id[-1] = []
                finding_reviews_by_id[-1].append(FindingReview(-1, review.reviewer, review.comment, "No", set()))

        for finding_id, finding_reviews in finding_reviews_by_id.items():
            output_entry = [detector, project_id, version_id, misuse_id]
            for finding_review in finding_reviews:
                comment = finding_review.comment.replace("\n", "").replace("\t", "")
                finding_name = "finding-" + str(finding_id)
                violations = ", ".join(finding_review.violations)
                output_entry += [finding_review.reviewer, comment, finding_name, finding_review.assessment, violations]
            output.append(output_entry)

    return output


def _write_tsv(file_path, output):
    lines = ["\t".join(entry) for entry in output]
    lines.sort()
    content = "\n".join(lines)
    safe_write(content, file_path, append=False)
