import getpass
import logging

from typing import List, Dict
from urllib.parse import urljoin

from requests import RequestException

from data.detector import Detector
from data.detector_run import DetectorRun
from data.finding import SpecializedFinding
from data.project import Project
from data.project_version import ProjectVersion
from data.version_compile import VersionCompile
from tasks.implementations.findings_filters import PotentialHits
from utils.web_util import post, as_markdown

_SNIPPETS_KEY = "target_snippets"


class PublishFindingsTask:
    def __init__(self, experiment_id: str, compiles_base_path: str, run_timestamp: int,
                 review_site_url: str, review_site_user: str= "", review_site_password: str= ""):
        super().__init__()
        self.max_files_per_post = 20  # 20 is PHP's default limit to the number of files per request

        self.experiment_id = experiment_id
        self.compiles_base_path = compiles_base_path
        self.run_timestamp = run_timestamp
        self.review_site_url = review_site_url
        self.review_site_user = review_site_user
        self.review_site_password = review_site_password

        if self.review_site_user and not self.review_site_password:
            self.review_site_password = getpass.getpass(
                "Enter review-site password for '{}': ".format(self.review_site_user))

    def run(self, project: Project, version: ProjectVersion, detector_run: DetectorRun,
            potential_hits: PotentialHits, version_compile: VersionCompile, detector: Detector):
        logger = logging.getLogger("tasks.publish_findings.version")
        logger.info("Publishing findings of %s in %s on %s for upload to %s...",
                    detector, self.experiment_id, version, self.review_site_url)

        if detector_run.is_success():
            logger.info("Detector reported %s potential hits.", len(potential_hits.findings))
            result = "success"
        elif detector_run.is_error():
            logger.info("Detector produced an error.")
            result = "error"
        elif detector_run.is_timeout():
            logger.info("Detector timed out.")
            result = "timeout"
        else:
            logger.info("Detector was not run.")
            result = "not run"

        run_info = detector_run.get_run_info()
        specialized_potential_hits = self.__specialize(potential_hits, detector, detector_run, version_compile, logger)

        try:
            for potential_hits_slice in self.__slice_by_max_files_per_post(specialized_potential_hits):
                postable_data = self.__to_postable_data(run_info, result, potential_hits_slice)
                file_paths = self.__get_file_paths(potential_hits_slice)
                self.__post(project, version, detector, postable_data, file_paths)
        except RequestException as e:
            response = e.response
            if response:
                logger.error("%d %s: %s", response.status_code, response.reason, response.text)
            else:
                logger.error("%s", e)

    @staticmethod
    def __specialize(potential_hits, detector, detector_run, version_compile, logger):
        specialized_findings = []

        for finding in potential_hits.findings:
            specialize_finding = detector.specialize_finding(detector_run.findings_path, finding)

            snippets = finding.get_snippets(version_compile.original_sources_paths)
            if not snippets:
                logger.warning("No snippet found for %s:%s!", finding["file"], finding["method"])
            specialize_finding[_SNIPPETS_KEY] = snippets

            specialized_findings.append(specialize_finding)

        return specialized_findings

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

    def __to_postable_data(self, run_info, result, potential_hits_slice: List[SpecializedFinding]):
        postable_potential_hits = []

        for potential_hit in potential_hits_slice:
            postable_data = self._to_markdown_dict(potential_hit)
            postable_data[_SNIPPETS_KEY] = [snippet.__dict__ for snippet in (potential_hit[_SNIPPETS_KEY])]
            postable_potential_hits.append(postable_data)

        data = self._to_markdown_dict(run_info)
        data["result"] = result
        data["potential_hits"] = postable_potential_hits
        data["timestamp"] = self.run_timestamp

        return data

    @staticmethod
    def _to_markdown_dict(finding: SpecializedFinding) -> Dict[str, str]:
        markdown_dict = dict()
        for key, value in finding.items():
            if key != _SNIPPETS_KEY:
                markdown_dict[key] = as_markdown(value)
        return markdown_dict

    @staticmethod
    def __get_file_paths(findings: List[SpecializedFinding]) -> List[str]:
        files = []
        for finding in findings:
            files.extend(finding.files)
        return files

    def __post(self, project, version, detector, postable_data, file_paths):
        url = self.__get_publish_findings_url(detector, project, version)
        post(url, postable_data, file_paths=file_paths,
             username=self.review_site_user, password=self.review_site_password)

    def __get_publish_findings_url(self, detector, project, version):
        experiment_id = self.experiment_id[2:]  # the review site uses only the experiment number as Id
        return urljoin(self.review_site_url, "experiments/{}/detectors/{}/projects/{}/versions/{}/runs".format(
            experiment_id, detector.id, project.id, version.version_id))
