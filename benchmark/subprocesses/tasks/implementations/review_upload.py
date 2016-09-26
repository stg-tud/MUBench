import json
import logging
from os.path import join, dirname, basename
from typing import Dict, Iterable, Tuple, IO
from typing import List

import requests

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.requirements import JavaRequirement, RequestsRequirement
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.subprocesses.tasks.implementations.detect import Run


class Request:
    def __init__(self, dataset: str, detector: Detector, project: Project,
                 version: ProjectVersion, findings: List[Dict]):
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
    URL_EX1 = "/upload/ex1"  # TODO
    URL_EX2 = "/upload/ex2"
    URL_EX3 = "/upload/ex3"

    def __init__(self, experiment: Experiment, dataset: str, detector: Detector, checkout_base_dir: str):
        super().__init__()
        self.experiment = experiment  # type: Experiment
        self.dataset = dataset  # type: str
        self.detector = detector  # type: Detector
        self.checkout_base_dir = checkout_base_dir  # type: str

        self.request_data = []  # type: List[Request]
        self.request_files = []  # type: List[RequestFile]

    def get_requirements(self):
        return [RequestsRequirement()]

    def start(self):
        logger = logging.getLogger("review_prepare")
        logger.info("Preparing review for results of %s...", self.detector)

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        logger = logging.getLogger("review_prepare.misuse")

        detector_run = self._get_run(version)

        if not detector_run.is_success():
            logger.info("Skipping %s in %s: no result.", misuse.misuse_id, version)
            return Response.skip

        logger.debug("Checking hit for %s in %s...", misuse, version)

        findings = detector_run.findings
        potential_hits = self.find_potential_hits(findings, misuse)

        if self.experiment == 2:
            matches = []
            for finding in potential_hits:
                for pattern in misuse.patterns:
                    if pattern.class_name in finding["pattern"]:
                        matches.append(finding)
                        break
            potential_hits = matches

        logger.info("Found %s potential hits for %s.", len(potential_hits), misuse)
        data = Request(self.dataset, self.detector, project, version, potential_hits)
        files = []  # TODO generate additional files (e.g. images for dot graphs)

        self.request_data.append(data)
        self.request_files.extend(files)

        return Response.ok

    def end(self):
        if self.experiment.id == "1":
            url = ReviewUpload.URL_EX1
        elif self.experiment.id == "2":
            url = ReviewUpload.URL_EX2
        elif self.experiment.id == "3":
            url = ReviewUpload.URL_EX3
        else:
            raise ValueError("Unknown experiment " + str(self.experiment))

        request_data = [data.__dict__ for data in self.request_data]
        data = json.dumps(request_data, sort_keys=True)
        files = [file.request_file_tuple for file in self.request_files]

        self.post(url, data, files)

    def _get_run(self, version: ProjectVersion) -> Run:
        return self.detector.get_run(self.experiment, version)

    @staticmethod
    def post(url: str, data: str, files: List[Tuple[str, Tuple[str, IO[bytes], str]]]) -> requests.Response:
        user = ""  # TODO set these values
        password = ""
        requests.post(url, auth=(user, password), data=data, files=files)

    @staticmethod
    def find_potential_hits(findings: Iterable[Dict[str, str]], misuse: Misuse) -> List[Dict[str, str]]:
        candidates = ReviewUpload.__filter_by_file(findings, misuse.location.file)
        candidates = ReviewUpload.__filter_by_method(candidates, misuse.location.method)
        return candidates

    @staticmethod
    def __filter_by_file(findings, misuse_file):
        matches = []
        for finding in findings:
            if ReviewUpload.__matches_file(finding["file"], misuse_file):
                matches.append(finding)
        return matches

    @staticmethod
    def __matches_file(finding_file, misuse_file):
        # If file is an inner class "Outer$Inner.class", the source file is "Outer.java".
        if "$" in finding_file:
            finding_file = finding_file.split("$", 1)[0] + ".java"
        # If file is a class file "A.class", the source file is "A.java".
        if finding_file.endswith(".class"):
            finding_file = finding_file[:-5] + "java"
        return finding_file.endswith(misuse_file)

    @staticmethod
    def __filter_by_method(findings, misuse_method):
        misuse_constructor = misuse_method.replace(misuse_method.split("(", 1)[0], "<init>")
        matches = []

        for finding in findings:
            if "method" in finding:
                method = finding["method"]
                # if detector reports only method names, this ensures we don't match prefixes of method names
                if "(" not in method:
                    method += "("
                if method in misuse_method or method in misuse_constructor:
                    matches.append(finding)
            else:
                # don't filter if the detector reports no method
                matches.append(finding)

        if not matches:
            # fall back to match without the signature
            for finding in findings:
                method = finding["method"].split("(")[0] + "("
                if method in misuse_method:
                    matches.append(finding)

        return matches
