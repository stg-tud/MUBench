import getpass
import logging
from sys import getsizeof
from typing import List, Dict
from urllib.parse import urljoin

import re

from os.path import getsize
from requests import RequestException

from data.detector import Detector
from data.detector_run import DetectorRun
from data.detector_specialising.specialising_util import replace_dot_graph_with_image
from data.finding import Finding
from data.project import Project
from data.project_version import ProjectVersion
from data.snippets import SnippetUnavailableException
from data.version_compile import VersionCompile
from tasks.implementations.findings_filters import PotentialHits
from utils.size import total_size
from utils.web_util import post, as_markdown

_SNIPPETS_KEY = "target_snippets"


class PublishFindingsTask:
    def __init__(self, experiment_id: str, compiles_base_path: str, review_site_url: str, review_site_user: str = "",
                 review_site_password: str = ""):
        super().__init__()
        self.max_files_per_post = 20  # 20 is PHP's default limit to the number of files per request
        self.max_post_size_in_bytes = 7000  # choose a moderate value since we only approximate upload size

        self.experiment_id = experiment_id
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
        logger.info("Publishing findings of %s in %s on %s for upload to %s...",
                    detector, self.experiment_id, version, self.review_site_url)

        if detector_run.is_success():
            logger.info("Uploading %s potential hits.", len(potential_hits.findings))
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
        postable_potential_hits = [
            self.__to_postable_potential_hit(potential_hit, version_compile, detector_run.findings_path, logger)
            for potential_hit in potential_hits.findings]

        try:
            for postable_potential_hits_slice in self.__slice_by_number_of_files_and_post_size(postable_potential_hits):
                file_paths = self.__get_file_paths(postable_potential_hits_slice)
                postable_data = self.__to_postable_data(run_info, result, postable_potential_hits_slice)
                self.__post(project, version, detector, postable_data, file_paths)
        except RequestException as e:
            response = e.response
            if response:
                logger.error("%d %s: %s", response.status_code, response.reason, response.text)
            else:
                logger.error("%s", e)

    def __slice_by_number_of_files_and_post_size(self, potential_hits: List['SpecializedFinding']) -> List[List[Finding]]:
        potential_hits_slice = []
        number_of_files_in_slice = 0
        size_of_slice = 0
        for potential_hit in potential_hits:
            number_of_files_in_hit = len(potential_hit.files)
            size_of_hit = self.__get_potential_hit_size(potential_hit)
            exceeds_max_files_per_post = number_of_files_in_slice + number_of_files_in_hit > self.max_files_per_post
            exceeds_max_post_size = size_of_slice + size_of_hit > self.max_post_size_in_bytes
            if potential_hits_slice and (exceeds_max_files_per_post or exceeds_max_post_size):
                yield potential_hits_slice
                potential_hits_slice = [potential_hit]
                number_of_files_in_slice = number_of_files_in_hit
                size_of_slice = size_of_hit
            else:
                potential_hits_slice.append(potential_hit)
                number_of_files_in_slice += number_of_files_in_hit
                size_of_slice += size_of_hit

        yield potential_hits_slice

    def __to_postable_data(self, run_info, result, postable_potential_hits: List[Dict]):
        data = self._to_markdown_dict(run_info)
        data["result"] = result
        data["potential_hits"] = postable_potential_hits

        return data

    def __to_postable_potential_hit(self, potential_hit: Finding, version_compile: VersionCompile,
                                    findings_path, logger) -> 'SpecializedFinding':
        postable_potential_hit = self._to_markdown_dict(potential_hit)
        files = self._convert_graphs_to_files(potential_hit, findings_path)
        postable_potential_hit[_SNIPPETS_KEY] = self.__get_postable_snippets(potential_hit, version_compile, logger)
        return SpecializedFinding(postable_potential_hit, files)

    @staticmethod
    def __get_postable_snippets(finding: Finding, version_compile: VersionCompile, logger) -> List[Dict]:
        return [snippet.__dict__ for snippet in PublishFindingsTask.__get_snippets(finding, version_compile, logger)]

    @staticmethod
    def __get_snippets(finding, version_compile, logger):
        try:
            return finding.get_snippets(version_compile.original_sources_paths)
        except SnippetUnavailableException as e:
            logger.warning(e)
            return []

    @staticmethod
    def _to_markdown_dict(finding: Finding) -> Dict[str, str]:
        markdown_dict = dict()
        for key, value in finding.items():
            if key != _SNIPPETS_KEY:
                markdown_dict[key] = as_markdown(value)
        return markdown_dict

    @staticmethod
    def __get_file_paths(findings: List['SpecializedFinding']) -> List[str]:
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

    @staticmethod
    def _convert_graphs_to_files(potential_hit: Dict, findings_path: str) -> List[str]:
        files = []

        graph_pattern = re.compile("(graph|digraph) .* {.*?}", re.DOTALL)
        for key, value in potential_hit.items():
            if type(value) is str and graph_pattern.match(value):
                files.append(replace_dot_graph_with_image(potential_hit, key, findings_path))

        return files

    @staticmethod
    def __get_potential_hit_size(potential_hit: 'SpecializedFinding') -> int:
        return getsizeof(potential_hit) + sum([getsize(file) for file in potential_hit.files])


class SpecializedFinding(Finding):
    def __init__(self, data: Dict[str, str], files: List[str] = None):
        super().__init__(data)
        self.files = files or []

    def __sizeof__(self):
        return total_size(self.__dict__) + total_size(self.files)
