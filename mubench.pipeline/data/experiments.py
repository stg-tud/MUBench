from os.path import join

from data.detector import Detector
from data.misuse import Misuse
from data.project_version import ProjectVersion
from data.run import Run
from data.detector_execution import DetectOnlyExecution, MineAndDetectExecution, DetectorMode
from data.findings_filters import PotentialHits, AllFindings


class Experiment:
    def __init__(self, experiment_id: str, detector: Detector, findings_base_path: str):
        self.id = experiment_id
        self.detector = detector
        self.findings_base_path = findings_base_path

    def get_run(self, version: ProjectVersion) -> Run:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class ProvidedPatternsExperiment(Experiment):
    ID = "ex1"

    def __init__(self, detector: Detector, findings_base_path: str):
        super().__init__(ProvidedPatternsExperiment.ID, detector, findings_base_path)

    def get_run(self, version: ProjectVersion):
        return Run([self.__create_execution(version, misuse) for misuse in version.misuses if misuse.patterns])

    def __create_execution(self, version, misuse):
        findings_filter = PotentialHits(self.detector, [misuse])
        return DetectOnlyExecution(self.detector, version, misuse, self.findings_base_path, findings_filter)

    def __str__(self):
        return "experiment 1 (provided patterns)"


class TopFindingsExperiment(Experiment):
    ID = "ex2"

    def __init__(self, detector: Detector, findings_base_path: str, limit: int = 0):
        super().__init__(TopFindingsExperiment.ID, detector, findings_base_path)
        self.limit = limit

    def get_run(self, version: ProjectVersion):
        findings_filter = AllFindings(self.detector, self.limit)
        return Run([MineAndDetectExecution(self.detector, version, self.findings_base_path, findings_filter)])

    def __str__(self):
        if self.limit:
            return "experiment 2 (top-{} findings)".format(self.limit)
        else:
            return "experiment 2 (all findings)"


class BenchmarkExperiment(Experiment):
    ID = "ex2"

    def __init__(self, detector: Detector, findings_base_path: str):
        super().__init__(BenchmarkExperiment.ID, detector, findings_base_path)

    def get_run(self, version: ProjectVersion):
        findings_filter = PotentialHits(self.detector, version.misuses)
        return Run([MineAndDetectExecution(self.detector, version, self.findings_base_path, findings_filter)])

    def __str__(self):
        return "experiment 3 (benchmark)"
