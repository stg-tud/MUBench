import getpass
import logging
from typing import List
from urllib.parse import urljoin

from requests import RequestException

from data.experiment import Experiment
from data.finding import SpecializedFinding
from data.project import Project
from data.project_version import ProjectVersion
from requirements import RequestsRequirement
from tasks.project_version_task import ProjectVersionTask
from utils.web_util import post


class PublishFindingsTask(ProjectVersionTask):
    def __init__(self, experiment: Experiment, dataset: str, compiles_base_path: str, review_site_url: str,
                 review_site_user: str= "", review_site_password: str= ""):
        super().__init__()
        self.max_files_per_post = 20  # 20 is PHP's default limit to the number of files per request

        self.experiment = experiment
        self.detector = experiment.detector
        self.dataset = dataset
        self.compiles_base_path = compiles_base_path
        self.review_site_url = review_site_url
        self.__upload_url = urljoin(self.review_site_url, "api/upload/" + self.experiment.id)
        self.review_site_user = review_site_user
        self.review_site_password = review_site_password

        self.logger = logging.getLogger("review_findings")

    def get_requirements(self):
        return [RequestsRequirement()]

    def start(self):
        if self.review_site_user and not self.review_site_password:
            self.review_site_password = getpass.getpass(
                "Enter review-site password for '{}': ".format(self.review_site_user))

        self.logger.info("Prepare findings of %s in %s for upload to %s...",
                         self.detector, self.experiment, self.__upload_url)

    def process_project_version(self, project: Project, version: ProjectVersion) -> List[str]:
        logger = self.logger.getChild("version")

        detector_run = self.experiment.get_run(version)
        runtime = detector_run.get_runtime()

        if detector_run.is_success():
            logger.info("Preparing findings in %s...", version)

            result = "success"
            number_of_findings = detector_run.get_number_of_findings()
            potential_hits = detector_run.get_potential_hits()

            logger.info("Found %s potential hits.", len(potential_hits))
        else:
            number_of_findings = 0
            potential_hits = []

            if detector_run.is_error():
                logger.info("Run on %s produced an error.", version)
                result = "error"
            elif detector_run.is_timeout():
                logger.info("Run on %s timed out.", version)
                result = "timeout"
            else:
                logger.info("Not run on %s.", version)
                result = "not run"

        logger.info("Extracting target source code...")
        version_compile = version.get_compile(self.compiles_base_path)
        for potential_hit in potential_hits:
            snippets = potential_hit.get_snippets(version_compile.original_sources_path)
            potential_hit["target_snippets"] = [snippet.__dict__ for snippet in snippets]

        try:
            logger.info("Publishing findings...")
            for potential_hits_slice in self.__slice_by_max_files_per_post(potential_hits):
                self.__post(project, version, runtime, number_of_findings, result, potential_hits_slice)
            logger.info("Findings published.")
        except RequestException as e:
            response = e.response
            if response:
                logger.error("ERROR: %d %s: %s", response.status_code, response.reason, response.text)
            else:
                logger.error("ERROR: %s", e)

        return self.ok()

    def __slice_by_max_files_per_post(self, potential_hits: List[SpecializedFinding]) -> List[List[SpecializedFinding]]:
        potential_hits_slice = []
        number_of_files_in_slice = 0
        for potential_hit in potential_hits:
            number_of_files_in_hit = len(potential_hit.files)
            if number_of_files_in_slice + number_of_files_in_hit > self.max_files_per_post:
                yield potential_hits_slice
                potential_hits_slice = [potential_hit]
                number_of_files_in_slice = number_of_files_in_hit
            else:
                potential_hits_slice.append(potential_hit)
                number_of_files_in_slice += number_of_files_in_hit

        yield potential_hits_slice

    def __post(self, project, version, runtime, number_of_findings, result, potential_hits):
        data = {
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": project.id,
            "version": version.version_id,
            "result": result,
            "runtime": runtime,
            "number_of_findings": number_of_findings,
            "potential_hits": potential_hits
        }
        file_paths = PublishFindingsTask.get_file_paths(potential_hits)
        post(self.__upload_url, data, file_paths=file_paths,
             username=self.review_site_user, password=self.review_site_password)

    @staticmethod
    def get_file_paths(findings: List[SpecializedFinding]) -> List[str]:
        files = []
        for finding in findings:
            files.extend(finding.files)
        return files
