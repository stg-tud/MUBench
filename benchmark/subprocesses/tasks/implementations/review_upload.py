import json
import logging
from os.path import join, basename

import requests
from typing import List
from typing import Tuple, IO

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark.data.finding import SpecializedFinding
from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.requirements import RequestsRequirement
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask


class RequestData:
    def __init__(self, dataset: str, detector: Detector, project: Project, version: ProjectVersion,
                 findings: List[SpecializedFinding]):
        super().__init__()
        self.detector_name = detector.id
        self.project = project.id
        self.version = version.version_id
        self.dataset = dataset
        self.findings = findings


class ReviewUpload(ProjectVersionMisuseTask):
    def __init__(self, experiment: Experiment, dataset: str, checkout_base_dir: str):
        super().__init__()
        self.experiment = experiment
        self.dataset = dataset
        self.detector = experiment.detector
        self.checkout_base_dir = checkout_base_dir

        self.data = []  # type: List[RequestData]

    def get_requirements(self):
        return [RequestsRequirement()]

    def start(self):
        logger = logging.getLogger("review_prepare")
        logger.info("Preparing review for results of %s...", self.detector)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        logger = logging.getLogger("review_prepare.misuse")

        detector_run = self.experiment.get_run(version)

        if not detector_run.is_success():
            logger.info("Skipping %s in %s: no result.", misuse.misuse_id, version)
            return Response.skip

        logger.debug("Checking hit for %s in %s...", misuse, version)
        run = self.experiment.get_run(version)
        findings = run.results()

        logger.info("Found %s potential hits for %s.", len(findings), misuse)
        data = RequestData(self.dataset, self.detector, project, version, findings)
        self.data.append(data)

        return Response.ok

    def end(self):
        url = "/upload/" + self.experiment.id
        file_paths = self.get_file_paths(self.data)
        self.post(url, self.__serialize_data(), file_paths)

    def __serialize_data(self) -> str:
        return json.dumps([d.__dict__ for d in self.data], sort_keys=True)

    @staticmethod
    def get_file_paths(data: List[RequestData]) -> List[str]:
        files = []
        findings = []
        for data in data:
            findings.extend(data.findings)
        for finding in findings:
            files.extend(finding.files)
        return files

    @staticmethod
    def post(url: str, data: str, file_paths: List[str]) -> requests.Response:
        user = ""  # TODO set these values
        password = ""
        files = [ReviewUpload._get_request_file_tuple(path) for path in file_paths]
        requests.post(url, auth=(user, password), data=data, files=files)

    @staticmethod
    def _get_request_file_tuple(path) -> Tuple[str, Tuple[str, IO[bytes], str]]:
        name = basename(path)
        return name, (name, open(join(path), 'rb'), "image/png")  # TODO make MIME type a parameter
