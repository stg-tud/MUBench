import json
import logging
from os.path import join, dirname, basename
from typing import Dict, Tuple, IO
from typing import List

import requests

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark.data.finding import SpecializedFinding
from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.requirements import RequestsRequirement
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask


class Request:
    def __init__(self, dataset: str, detector: Detector, project: Project,
                 version: ProjectVersion, findings: List[SpecializedFinding]):
        self.detector_name = detector.id
        self.project = project.id
        self.version = version.version_id
        self.dataset = dataset
        self.findings = findings


class RequestFile:
    def __init__(self, path: str):
        self.name = basename(path)
        self.path = dirname(path)

    @property
    def request_file_tuple(self) -> Tuple[str, Tuple[str, IO[bytes], str]]:
        return self.name, (self.name, self.__stream, self.path)

    @property
    def __stream(self) -> IO[bytes]:
        return open(join(self.path, self.name), 'rb')


class ReviewUpload(ProjectVersionMisuseTask):
    def __init__(self, experiment: Experiment, dataset: str, checkout_base_dir: str):
        super().__init__()
        self.experiment = experiment
        self.dataset = dataset
        self.detector = experiment.detector
        self.checkout_base_dir = checkout_base_dir

        self.data = []  # type: List[Request]

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
        data = Request(self.dataset, self.detector, project, version, findings)
        self.data.append(data)

        return Response.ok

    def end(self):
        url = "/upload/" + self.experiment.id
        request_data = []  # TODO serialize self.data
        files = []

        data = json.dumps(request_data, sort_keys=True)
        self.post(url, data, files)

    @staticmethod
    def post(url: str, data: str, files: List[Tuple[str, Tuple[str, IO[bytes], str]]]) -> requests.Response:
        user = ""  # TODO set these values
        password = ""
        requests.post(url, auth=(user, password), data=data, files=files)
