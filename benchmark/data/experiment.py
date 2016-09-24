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
    PROVIDED_PATTERNS = "1"
    TOP_FINDINGS = "2"
    BENCHMARK = "3"
    ALL = [PROVIDED_PATTERNS, TOP_FINDINGS, BENCHMARK]

    RUN_MODES = {
        PROVIDED_PATTERNS: DetectorMode.detect_only,
        TOP_FINDINGS: DetectorMode.mine_and_detect,
        BENCHMARK: DetectorMode.mine_and_detect
    }

    def __init__(self, experiment_id: str, findings_path: str, reviews_path: str):
        if experiment_id not in Experiment.ALL:
            raise ValueError("no such experiment: {}".format(experiment_id))

        self.id = experiment_id
        self.findings_path = join(findings_path, str(int(self.detector_mode)))
        self.reviews_path = join(reviews_path, self.id)

    def get_findings_path(self, detector: Detector):
        return join(self.findings_path, detector.id)

    def get_run(self, detector: Detector, version: ProjectVersion):
        return Run(join(self.get_findings_path(detector), version.project_id, version.version_id))

    def get_review_dir(self, version: ProjectVersion, misuse: Misuse = None):
        if self.id == Experiment.TOP_FINDINGS:
            return join(version.project_id, version.version_id)
        else:
            return join(version.project_id, version.version_id, misuse.misuse_id)

    def get_review_path(self, detector: Detector, version: ProjectVersion, misuse: Misuse = None):
        return join(self.reviews_path, detector.id, self.get_review_dir(version, misuse))

    @property
    def detector_mode(self) -> DetectorMode:
        return Experiment.RUN_MODES.get(self.id)
