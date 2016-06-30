import logging
from os.path import join
from typing import Dict, Iterable

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.subprocesses.tasks.implementations.detect import Run
from benchmark.utils.io import safe_open


class Evaluate(ProjectVersionMisuseTask):
    no_hit = 0
    potential_hit = 1

    def __init__(self, results_path: str, detector_result_file: str, checkout_base_dir: str, eval_result_file: str):
        super().__init__()
        self.results_path = results_path
        self.detector_result_file = detector_result_file
        self.checkout_base_dir = checkout_base_dir
        self.eval_result_file = eval_result_file

        self.results = []

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:
        logger = logging.getLogger("evaluate")
        logger.debug("Checking hit for %s in %s...", misuse, version)

        result_path = join(self.results_path, project.id, version.version_id)
        detector_run = Run(result_path)

        findings = detector_run.findings

        if Evaluate.__is_file_found(findings, misuse):
            logger.info("Found potential hit for %s.", misuse)
            self.results.append((misuse.id, Evaluate.potential_hit))
        else:
            logger.info("No hit for %s.", misuse)
            self.results.append((misuse.id, Evaluate.no_hit))

        return Response.ok

    def teardown(self):
        with safe_open(join(self.results_path, self.eval_result_file), 'w+') as file_result:
            for result in self.results:
                print(str(result).lstrip('(').rstrip(')'), file=file_result)

    @staticmethod
    def __is_file_found(findings: Iterable[Dict[str, str]], misuse: Misuse) -> bool:
        logger = logging.getLogger("evaluate.compare")

        misuse_file = misuse.location.file
        for finding in findings:
            if "file" in finding:
                finding_file = finding["file"]
                # If file is an inner class "Outer$Inner.class", the source file is "Outer.java".
                if "$" in finding_file:
                    finding_file = finding_file.split("$", 1)[0] + ".java"
                # If file is a class file "A.class", the source file is "A.java".
                if finding_file.endswith(".class"):
                    finding_file = finding_file[:-5] + "java"

                if finding_file.endswith(misuse_file):
                    logger.debug("Detector found something in '%s'.", misuse_file)
                    return True

        logger.debug("Detector found nothing in '%s'.", misuse_file)
        return False
