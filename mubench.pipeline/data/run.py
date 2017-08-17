from logging import Logger

from typing import List, Optional

from data.finding import SpecializedFinding, Finding
from data.detector_execution import DetectorExecution


class Run:
    def __init__(self, run_executions: List[DetectorExecution]):
        self.executions = run_executions

    def execute(self, compile_base_path: str, timeout: Optional[int], logger: Logger):
        if not self.executions:
            logger.info("Nothing to run.")
        else:
            for execution in self.executions:
                execution.execute(compile_base_path, timeout, logger)

    def get_potential_hits(self) -> List[SpecializedFinding]:
        potential_hits = []

        if self.is_success():
            previous_execution_min_rank = 0
            for execution in self.executions:
                min_rank = previous_execution_min_rank
                for potential_hit in execution.potential_hits:
                    rank = int(potential_hit["rank"])
                    if rank < min_rank:
                        rank += previous_execution_min_rank
                    potential_hit["rank"] = rank
                    potential_hits.append(potential_hit)
                    min_rank = rank + 1
                previous_execution_min_rank = min_rank

        return potential_hits

    def get_number_of_findings(self) -> int:
        number_of_findings = 0
        for execution in self.executions:
            number_of_findings += execution.number_of_findings
        return number_of_findings

    def get_runtime(self):
        runtime = 0
        for execution in self.executions:
            runtime += execution.runtime
        return runtime / len(self.executions)

    def get_run_info(self):
        run_info = {
            "number_of_findings": self.get_number_of_findings(),
            "runtime": self.get_runtime()
        }
        if self.executions:
            run_info.update(self.executions[0].get_run_info())
        return run_info

    def reset(self):
        for execution in self.executions:
            execution.reset()

    def __str__(self):
        return "run on {}".format(self.executions[0].version)

    def is_success(self):
        return self.executions and all([execution.is_success() for execution in self.executions])

    def is_outdated(self):
        return self.executions and any([execution.is_outdated() for execution in self.executions])

    def is_error(self):
        return self.executions and any([execution.is_error() for execution in self.executions])

    def is_timeout(self):
        return self.executions and any([execution.is_timeout() for execution in self.executions])

    def is_failure(self):
        return self.is_error() or self.is_timeout()
