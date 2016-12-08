import getpass
import logging
from typing import List
from urllib.parse import urljoin

from requests import HTTPError

from benchmark.data.experiment import Experiment
from benchmark.data.finding import SpecializedFinding
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.requirements import RequestsRequirement
from benchmark.tasks.project_version_task import ProjectVersionTask
from benchmark.utils.web_util import post


class PublishFindingsTask(ProjectVersionTask):
    def __init__(self, experiment: Experiment, dataset: str, review_site_url: str, review_site_user: str= ""):
        super().__init__()
        self.experiment = experiment
        self.detector = experiment.detector
        self.dataset = dataset
        self.review_site_url = review_site_url
        self.__upload_url = urljoin(self.review_site_url, "api/upload/" + self.experiment.id)
        self.review_site_user = review_site_user
        self.review_site_user_password = ""

        self.logger = logging.getLogger("review_findings")

    def get_requirements(self):
        return [RequestsRequirement()]

    def start(self):
        if self.review_site_user:
            self.review_site_user_password = getpass.getpass(
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
            number_of_findings = len(detector_run.get_findings())
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

        for potential_hit in potential_hits:
            potential_hit["target_snippets"] = [snippet.__dict__ for snippet in potential_hit.get_snippets()]

        try:
            self.__post(project, version, runtime, number_of_findings, result, potential_hits)
            logger.info("Findings published.")
        except HTTPError as e:
            logger.error("Failed to publish findings: %s", e)

        return self.ok()

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
             username=self.review_site_user, password=self.review_site_user_password)

    @staticmethod
    def get_file_paths(findings: List[SpecializedFinding]) -> List[str]:
        files = []
        for finding in findings:
            files.extend(finding.files)
        return files
