from os.path import join

from benchmark.data.detector import Detector
from benchmark.data.misuse import Misuse
from benchmark.data.project_version import ProjectVersion
from benchmark.data.run import Run
from benchmark.data.detector_execution import DetectOnlyExecution, MineAndDetectExecution, DetectorMode
from benchmark.data.findings_filters import PotentialHits, AllFindings


class Experiment:
    PROVIDED_PATTERNS = "ex1"
    TOP_FINDINGS = "ex2"
    BENCHMARK = "ex3"

    def __init__(self, experiment_id: str, detector: Detector, findings_base_path: str, reviews_path: str):
        self.id = experiment_id
        self.detector = detector
        self.findings_base_path = findings_base_path
        self.reviews_path = join(reviews_path, self.id, self.detector.id)

    def get_run(self, version: ProjectVersion) -> Run:
        if self.id == Experiment.PROVIDED_PATTERNS:
            executions = [
                DetectOnlyExecution(self.detector, version, misuse, self.findings_base_path,
                                    PotentialHits(self.detector, [misuse])) for
                misuse in version.misuses]
        elif self.id == Experiment.TOP_FINDINGS:
            executions = [
                MineAndDetectExecution(self.detector, version, self.findings_base_path, AllFindings(self.detector))]
        elif self.id == Experiment.BENCHMARK:
            executions = [MineAndDetectExecution(self.detector, version, self.findings_base_path,
                                                 PotentialHits(self.detector, version.misuses))]
        else:
            executions = []

        return Run(executions)

    def get_review_dir(self, version: ProjectVersion, misuse: Misuse = None):
        if self.id == Experiment.TOP_FINDINGS:
            return join(version.project_id, version.version_id)
        else:
            return join(version.project_id, version.version_id, misuse.misuse_id)

    def get_review_path(self, version: ProjectVersion, misuse: Misuse = None):
        return join(self.reviews_path, self.get_review_dir(version, misuse))

    def __str__(self):
        if self.id == Experiment.PROVIDED_PATTERNS:
            return "experiment 1 (provided patterns)"
        elif self.id == Experiment.TOP_FINDINGS:
            return "experiment 2 (top findings)"
        elif self.id == Experiment.BENCHMARK:
            return "experiment 3 (benchmark)"
