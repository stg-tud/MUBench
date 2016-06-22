from typing import Iterable

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.visualize_results import Grouping


# noinspection PyPep8Naming
class project(Grouping):
    def get_groups(self, misuse: Misuse) -> Iterable[str]:
        return [misuse.project_name]


class synthetic(Grouping):
    def get_groups(self, misuse: Misuse) -> Iterable[str]:
        return ["synthetic" if "synthetic" in misuse.name else "not synthetic"]


class characteristic(Grouping):
    def get_groups(self, misuse: Misuse) -> Iterable[str]:
        return misuse.meta.get("characteristics", ["unknown"])
