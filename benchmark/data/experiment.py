from enum import IntEnum
from os.path import join

from benchmark.data.detector import Detector
from benchmark.data.misuse import Misuse
from benchmark.data.project_version import ProjectVersion
from benchmark.data.run import Run


class DetectorMode(IntEnum):
    mine_and_detect = 0
    detect_only = 1


class Experiment:
    PROVIDED_PATTERNS = "ex1"
    TOP_FINDINGS = "ex2"
    BENCHMARK = "ex3"

    RUN_MODES = {
        PROVIDED_PATTERNS: DetectorMode.detect_only,
        TOP_FINDINGS: DetectorMode.mine_and_detect,
        BENCHMARK: DetectorMode.mine_and_detect
    }

    def __init__(self, experiment_id: str, detector: Detector, findings_path: str, reviews_path: str):
        self.id = experiment_id
        self.detector = detector
        self.findings_path = join(findings_path, self.detector_mode.name, self.detector.id)
        self.reviews_path = join(reviews_path, self.id, self.detector.id)

    def get_run(self, version: ProjectVersion):
        return Run(join(self.findings_path, version.project_id, version.version_id), version)

    def get_review_dir(self, version: ProjectVersion, misuse: Misuse = None):
        if self.id == Experiment.TOP_FINDINGS:
            return join(version.project_id, version.version_id)
        else:
            return join(version.project_id, version.version_id, misuse.misuse_id)

    def get_review_path(self, version: ProjectVersion, misuse: Misuse = None):
        return join(self.reviews_path, self.get_review_dir(version, misuse))

    @property
    def detector_mode(self) -> DetectorMode:
        return Experiment.RUN_MODES.get(self.id)
