import getpass
import logging
from typing import List, Dict
from urllib.parse import urljoin

from requests import RequestException

from data.detector import Detector
from data.detector_run import DetectorRun
from data.finding import SpecializedFinding, Finding
from data.project import Project
from data.version_compile import VersionCompile
from data.project_version import ProjectVersion
from tasks.implementations.findings_filters import PotentialHits
from utils.web_util import post, as_markdown


class PublishFindingsTask:
    def __init__(self, experiment_id: str, dataset: str, compiles_base_path: str,
                 review_site_url: str, review_site_user: str= "", review_site_password: str= ""):
        super().__init__()
        self.max_files_per_post = 20  # 20 is PHP's default limit to the number of files per request

        self.experiment_id = experiment_id
        self.dataset = dataset
        self.compiles_base_path = compiles_base_path
        self.review_site_url = review_site_url
        self.review_site_user = review_site_user
        self.review_site_password = review_site_password

        if self.review_site_user and not self.review_site_password:
            self.review_site_password = getpass.getpass(
                "Enter review-site password for '{}': ".format(self.review_site_user))

    def run(self, project: Project, version: ProjectVersion, detector_run: DetectorRun,
            potential_hits: PotentialHits, version_compile: VersionCompile, detector: Detector):
        logger = logging.getLogger("tasks.publish_findings.version")
        logger.info("Prepare findings of %s in %s for upload to %s...",
                    detector, self.experiment_id, self.review_site_url)

        run_info = detector_run.get_run_info()

        if detector_run.is_success():
            logger.info("Preparing findings in %s...", version)
            result = "success"
            logger.info("Found %s potential hits.", len(potential_hits.findings))
        else:
            if detector_run.is_error():
                logger.info("Run on %s produced an error.", version)
                result = "error"
            elif detector_run.is_timeout():
                logger.info("Run on %s timed out.", version)
                result = "timeout"
            else:
                logger.info("Not run on %s.", version)
                result = "not run"

        try:
            logger.info("Publishing potential hits...")
            for potential_hits_slice in self.__slice_by_max_files_per_post(potential_hits.findings):
                post_data_slice = []
                for potential_hit in potential_hits_slice:
                    postable_data = self._prepare_post(potential_hit, detector, detector_run.findings_path,
                                                       version_compile, logger)
                    post_data_slice.append(postable_data)

                file_paths = PublishFindingsTask.get_file_paths(potential_hits_slice)
                self.__post(project, version, detector, run_info, result, post_data_slice, file_paths)
            logger.info("Potential hits published.")
        except RequestException as e:
            response = e.response
            if response:
                logger.error("ERROR: %d %s: %s", response.status_code, response.reason, response.text)
            else:
                logger.error("ERROR: %s", e)

    def __slice_by_max_files_per_post(self, potential_hits: List[Finding]) -> List[List[Finding]]:
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

    def _prepare_post(self, finding: Finding, detector: Detector, findings_path: str, version_compile: VersionCompile,
                      logger) -> Dict[str, str]:
        specialized_finding = detector.specialize_finding(findings_path, finding)
        markdown_dict = self._to_markdown_dict(specialized_finding)

        snippets = finding.get_snippets(version_compile.original_sources_paths)
        if not snippets:
            logger.warning("No snippets added.")

        markdown_dict["target_snippets"] = [snippet.__dict__ for snippet in snippets]
        return markdown_dict

    def __post(self, project, version, detector, run_info, result, upload_data, file_paths):
        data = {}
        data.update(self._to_markdown_dict(run_info))
        data.update({
            "result": result,
            "potential_hits": upload_data
        })
        url = urljoin(self.review_site_url, "experiments/{}/detectors/{}/projects/{}/versions/{}/runs".format(
            self.experiment_id, detector.id, project.id, version.version_id))
        post(url, data, file_paths=file_paths, username=self.review_site_user, password=self.review_site_password)

    @staticmethod
    def get_file_paths(findings: List[SpecializedFinding]) -> List[str]:
        files = []
        for finding in findings:
            files.extend(finding.files)
        return files

    def _to_markdown_dict(self, finding: SpecializedFinding) -> Dict[str, str]:
        markdown_dict = dict()
        for key, value in finding.items():
            markdown_dict[key] = as_markdown(value)
        return markdown_dict

