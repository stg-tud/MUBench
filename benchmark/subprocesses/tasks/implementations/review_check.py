from os import listdir
from os.path import join, exists
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
    def __init__(self, finding_id: int, reviewer: str, assessment: str, violations: Set[str]):
        self.finding_id = finding_id
        self.reviewer = reviewer
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
                    self.findings.append(FindingReview(hit["id"], self.reviewer, "Yes", hit.get("vts", [])))
            else:
                for finding in data["findings"]:
                    self.findings.append(
                        FindingReview(finding["id"], self.reviewer, finding["assessment"], finding["violations"]))


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

        if not exists(join(review_path, "review.php")):
            return

        reviews = self.__get_reviews(review_path)

        output_header = [detector, project.id, version.version_id, misuse.id]
        finding_reviews_by_id = {}  # type: Dict[int,List[FindingReview]]
        for review in reviews:
            output_header += [review.reviewer, review.comment.replace("\n", ""), "", ""]

            for finding_review in review.findings:
                if finding_review.finding_id not in finding_reviews_by_id:
                    finding_reviews_by_id[finding_review.finding_id] = []
                finding_reviews_by_id[finding_review.finding_id].append(finding_review)
        self.output.append(output_header)

        for finding_id, finding_reviews in finding_reviews_by_id.items():
            output_entry = [detector, project.id, version.version_id, misuse.id]
            for finding_review in finding_reviews:
                output_entry += [finding_review.reviewer, "finding-" + str(finding_id), finding_review.assessment,
                                 ", ".join(finding_review.violations)]

            self.output.append(output_entry)

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

        if not exists(review_path) or not listdir(review_path):
            return

        reviews = self.__get_reviews(review_path)

        output_header = [detector, project.id, version.version_id]
        finding_reviews_by_id = {}  # type: Dict[int,List[FindingReview]]
        for review in reviews:
            output_header += [review.reviewer, review.comment.replace("\n", ""), "", ""]

            for finding_review in review.findings:
                if finding_review.finding_id not in finding_reviews_by_id:
                    finding_reviews_by_id[finding_review.finding_id] = []
                finding_reviews_by_id[finding_review.finding_id].append(finding_review)
        self.output.append(output_header)

        for finding_id, finding_reviews in finding_reviews_by_id.items():
            output_entry = [detector, project.id, version.version_id]
            for finding_review in finding_reviews:
                output_entry += [finding_review.reviewer, "finding-" + str(finding_id), finding_review.assessment,
                                 ", ".join(finding_review.violations)]

            self.output.append(output_entry)

    @staticmethod
    def __get_reviews(review_path: str) -> List[Review]:
        return [Review(join(review_path, file)) for file in listdir(review_path) if
                file.startswith('finding-') and file.endswith('.yml')]

    def end(self):
        _write_tsv(join(self.review_path, self.experiment + "-summary.csv"), self.output)


def _write_tsv(file_path, output):
    lines = ["\t".join(entry) for entry in output]
    lines.sort()
    content = "\n".join(lines)
    safe_write(content, file_path, append=False)
