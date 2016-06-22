from benchmark.data.misuse import Misuse
from benchmark.subprocesses.visualize_results import Grouping


# noinspection PyPep8Naming
class project(Grouping):
    def get(self, misuse: Misuse) -> str:
        return misuse.project_name
