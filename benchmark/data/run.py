from logging import Logger

from typing import List, Optional

from benchmark.data.finding import SpecializedFinding
from benchmark.data.detector_execution import DetectorExecution


class Run:
    def __init__(self, run_executions: List[DetectorExecution]):
        self.executions = run_executions

    def execute(self, compile_base_path: str, timeout: Optional[int], logger: Logger):
        for execution in self.executions:
            execution.execute(compile_base_path, timeout, logger)

    def results(self) -> List[SpecializedFinding]:
        potential_hits = []
        for execution in self.executions:
            potential_hits.extend(execution.potential_hits)
        return potential_hits

    def save(self):
        for execution in self.executions:
            execution.save()

    def reset(self):
        for execution in self.executions:
            execution.reset()

    def __str__(self):
        return "run on {}".format(", ".join([str(e) for e in self.executions]))

    def is_success(self):
        return self.executions and all([execution.state.is_success() for execution in self.executions])

    def is_outdated(self):
        return any([execution.state.is_outdated() for execution in self.executions])

    def is_error(self):
        return any([execution.state.is_error() for execution in self.executions])

    def is_timeout(self):
        return any([execution.state.is_timeout() for execution in self.executions])

    def is_failure(self):
        return self.is_error() or self.is_timeout()
