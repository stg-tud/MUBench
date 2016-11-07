import json
import logging
from os.path import join, basename
from typing import Dict
from typing import List
from typing import Tuple, IO
from urllib.parse import urljoin

import requests

from benchmark.data.experiment import Experiment
from benchmark.data.finding import SpecializedFinding
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.requirements import RequestsRequirement
from benchmark.tasks.project_version_task import ProjectVersionTask


class PublishFindingsTask(ProjectVersionTask):
    def __init__(self, experiment: Experiment, dataset: str, review_site_url: str):
        super().__init__()
        self.experiment = experiment
        self.detector = experiment.detector
        self.dataset = dataset
        self.review_site_url = review_site_url

        self.logger = logging.getLogger("review_findings")
        self.__review_data = []  # type: List[Dict]
        self.__files_paths = []  #type: List[str]

    def get_requirements(self):
        return [RequestsRequirement()]

    def start(self):
        self.logger.info("Prepare findings of %s in %s...", self.detector, self.experiment)

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

        self.__review_data.append({
            "dataset": self.dataset,
            "detector": self.detector.id,
            "project": project.id,
            "version": version.version_id,
            "result": result,
            "runtime": runtime,
            "number_of_findings": number_of_findings,
            "potential_hits": potential_hits
        })
        self.__files_paths.extend(PublishFindingsTask.get_file_paths(potential_hits))

        return self.ok()

    def end(self):
        if not self.__review_data:
            self.logger.info("Nothing to upload.")
        else:
            url = urljoin(self.review_site_url, "upload/" + self.experiment.id)
            self.logger.info("Uploading to %s...", url)
            self.post(url, self.__review_data, self.__files_paths)

    @staticmethod
    def get_file_paths(findings: List[SpecializedFinding]) -> List[str]:
        files = []
        for finding in findings:
            files.extend(finding.files)
        return files

    @staticmethod
    def post(url: str, data: List[Dict], file_paths: List[str]) -> requests.Response:
        user = ""  # TODO set these values
        password = ""
        files = [PublishFindingsTask._get_request_file_tuple(path) for path in file_paths]
        serialized_data = json.dumps([d for d in data], sort_keys=True)
        requests.post(url, auth=(user, password), data=serialized_data, files=files)

    @staticmethod
    def _get_request_file_tuple(path) -> Tuple[str, Tuple[str, IO[bytes], str]]:
        name = basename(path)
        return name, (name, open(join(path), 'rb'), "image/png")  # TODO make MIME type a parameter
