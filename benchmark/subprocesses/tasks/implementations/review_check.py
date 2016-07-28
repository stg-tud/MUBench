import logging
import yaml
from functools import reduce
from os import listdir
from os.path import join, exists, basename
from typing import List, Dict
from typing import Set

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.utils.io import read_yaml


class ReviewCheck(ProjectVersionMisuseTask):
    problems = {}

    MIN_REVIEWS = 2

    class ReviewedHit:
        def __init__(self, review_file: str, hit_id: int, reviewer: str, characteristics: Set[str]):
            self.review_file = review_file
            self.hit_id = hit_id
            self.reviewer = reviewer
            self.characteristics = characteristics

    def __init__(self, review_path: str, detectors: List[str]):
        super().__init__()
        self.review_path = review_path
        self.detectors = detectors

    def start(self):
        for detector in self.detectors:
            ReviewCheck.problems[detector] = {}

    def process_project(self, project: Project):
        for detector in self.detectors:
            ReviewCheck.problems[detector][project.id] = {}
        super().process_project(project)

    def process_project_version(self, project: Project, version: ProjectVersion):
        for detector in self.detectors:
            ReviewCheck.problems[detector][project.id][version.version_id] = {}
        super().process_project_version(project, version)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        for detector in self.detectors:
            self.process_detector_project_version_misuse(detector, project, version, misuse)
        return Response.ok

    def process_detector_project_version_misuse(self, detector: str, project: Project, version: ProjectVersion,
                                                misuse: Misuse):
        ReviewCheck.problems[detector][project.id][version.version_id][misuse.misuse_id] = {}
        review_path = join(self.review_path, detector, project.id, version.version_id, misuse.id)
        review_html = exists(join(review_path, 'review.html'))
        potential_hits_yml = exists(join(review_path, 'potentialhits.yml'))
        if not review_html or not potential_hits_yml:
            return
        reviewed_hits = self.__get_reviewed_hits(review_path)  # type: List[ReviewCheck.ReviewedHit]
        reviews_per_id = {}  # type: Dict[int, List[ReviewCheck.ReviewedHit]]
        for hit_id in self.__get_hit_ids(join(review_path, 'potentialhits.yml')):
            reviews_per_id[hit_id] = []
        for reviewed_hit in reviewed_hits:
            hit_id = reviewed_hit.hit_id

            problems = []
            ReviewCheck.problems[detector][project.id][version.version_id][misuse.misuse_id][hit_id] = problems

            if reviewed_hit.reviewer is None:
                problems.append('{}: unknown reviewer'.format(reviewed_hit.review_file))

            if hit_id in reviews_per_id:
                reviews_per_id[hit_id].append(reviewed_hit)
            else:
                problems.append('{}: unknown hit id {}'.format(reviewed_hit.review_file, hit_id))

        ReviewCheck.__check_enough_reviews_per_hit(reviews_per_id, detector, project, version, misuse)
        ReviewCheck.__check_same_characteristics(reviews_per_id, detector, project, version, misuse)

    def end(self):
        ReviewCheck.output_problems()

    @staticmethod
    def __check_enough_reviews_per_hit(reviews_per_id: Dict[int, List[ReviewedHit]], detector: str, project: Project,
                                       version: ProjectVersion, misuse: Misuse):
        ids_with_missing_reviews = ReviewCheck.__get_ids_with_missing_reviews(reviews_per_id)
        problems = ReviewCheck.problems[detector][project.id][version.version_id][misuse.misuse_id]
        for hit_id in ids_with_missing_reviews:
            message = 'missing {1} review(s) for hit {0}'.format(hit_id, ids_with_missing_reviews[hit_id])
            if hit_id in problems:
                problems[hit_id].append(message)
            else:
                problems[hit_id] = [message]

    @staticmethod
    def __check_same_characteristics(reviews_per_id: Dict[int, List[ReviewedHit]], detector: str, project: Project,
                                     version: ProjectVersion, misuse: Misuse):
        def symmetric_difference(a: Set[str], b: Set[str]) -> Set[str]:
            return (a - b).union(b - a)

        def to_characteristics(hit: ReviewCheck.ReviewedHit) -> Set[str]:
            return hit.characteristics

        problems = ReviewCheck.problems[detector][project.id][version.version_id][misuse.misuse_id]
        for hit_id in reviews_per_id:
            reviews = reviews_per_id[hit_id]
            if reviews:
                diff = reduce(symmetric_difference, map(to_characteristics, reviews))
                if diff:
                    message = 'differing characteristics: {}'.format(', '.join(sorted(diff)))
                    problems[hit_id].append(message)

    @staticmethod
    def __get_reviewed_hits(review_path: str) -> List[object]:
        review_files = [join(review_path, file) for file in listdir(review_path) if
                        file.startswith('review') and file.endswith('.yml')]
        reviewed_hits = []
        for review_file in review_files:
            review_yaml = read_yaml(review_file)
            reviewer = review_yaml.get('reviewer', None)
            for reviewed_hit in review_yaml.get('hits', []):
                hit_id = reviewed_hit.get('id', None)
                characteristics = set(reviewed_hit.get('characteristics', []))
                hit = ReviewCheck.ReviewedHit(basename(review_file), hit_id, reviewer, characteristics)
                reviewed_hits.append(hit)
        return reviewed_hits

    @staticmethod
    def __get_hit_ids(hits_file: str) -> List[int]:
        with open(hits_file) as file:
            return [hit['id'] for hit in yaml.load_all(file) if hit is not None]

    @staticmethod
    def __get_ids_with_missing_reviews(reviews_per_id: Dict[int, List[ReviewedHit]]) -> Dict[int, int]:
        ids = {}
        for hit_id in reviews_per_id:
            number_of_reviews = len(reviews_per_id[hit_id])
            if number_of_reviews < ReviewCheck.MIN_REVIEWS:
                ids[hit_id] = ReviewCheck.MIN_REVIEWS - number_of_reviews
        return ids

    @staticmethod
    def output_problems():
        for detector, projects in ReviewCheck.problems.items():
            for project, versions in projects.items():
                for version, misuses in versions.items():
                    for misuse, potential_hits in misuses.items():
                        for potential_hit, problems in potential_hits.items():
                            logger_name = 'review_check'
                            logger = logging.getLogger(logger_name)
                            logger.info('.'.join([detector, project, version, misuse, str(potential_hit)]))
                            for problem in problems:
                                logger.info('\t' + problem)
