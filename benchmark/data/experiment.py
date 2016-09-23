from enum import IntEnum
from os.path import join


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

    def __init__(self, experiment_id: str):
        if experiment_id not in Experiment.ALL:
            raise ValueError("no such experiment: {}".format(experiment_id))

        self.id = experiment_id

    def get_findings_path(self, findings_base_path):
        return join(findings_base_path, self.id)

    @property
    def detector_mode(self) -> DetectorMode:
        return Experiment.RUN_MODES.get(self.id)
