from os.path import join
from typing import Dict, List

from benchmark.data.detector import Detector
from benchmark.data.finding import Finding
from benchmark.data.misuse import Misuse
from benchmark.data.project_version import ProjectVersion
from benchmark.data.run import PerMisuseRun, VersionRun, Run


class RunResult:
    def __init__(self):
        self.potential_hits = {}  # type: Dict[Misuse, List[Finding]]
        self.files = []  # type: List[str]


class Experiment:
    PROVIDED_PATTERNS = "ex1"
    TOP_FINDINGS = "ex2"
    BENCHMARK = "ex3"

    def __init__(self, experiment_id: str, detector: Detector, findings_base_path: str, reviews_path: str):
        self.id = experiment_id
        self.detector = detector
        self.findings_base_path = findings_base_path
        self.reviews_path = join(reviews_path, self.id, self.detector.id)

    def get_run(self, version: ProjectVersion):
        if self.id == Experiment.PROVIDED_PATTERNS:
            return PerMisuseRun(self.detector, self.findings_base_path, version)
        else:
            return VersionRun(self.detector, self.findings_base_path, version)

    def get_review_dir(self, version: ProjectVersion, misuse: Misuse = None):
        if self.id == Experiment.TOP_FINDINGS:
            return join(version.project_id, version.version_id)
        else:
            return join(version.project_id, version.version_id, misuse.misuse_id)

    def get_review_path(self, version: ProjectVersion, misuse: Misuse = None):
        return join(self.reviews_path, self.get_review_dir(version, misuse))

    def get_run_results(self, run: Run) -> RunResult:
        result = RunResult()
        findings_path = run._get_findings_path()

        if self.id == Experiment.TOP_FINDINGS:
            findings = run.detector.specialize_findings(findings_path, run.findings)
            for finding in findings:
                misuse = Misuse("", run.version.project_id, "finding" + finding["id"])
                misuse.location.file = finding["file"]
                misuse.location.method = finding["method"]
                result.potential_hits[misuse] = [finding]
        else:
            for misuse in run.version.misuses:
                result.potential_hits[misuse] = self.detector.specialize_findings(findings_path,
                                                                                  run.get_potential_hits(misuse))

        result.files = run.detector.files_to_upload

        return result
