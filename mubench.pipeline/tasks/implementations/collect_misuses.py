from data.project_version import ProjectVersion
from utils.data_filter import DataFilter


class CollectMisusesTask:
    def __init__(self, data_filter: DataFilter):
        self.data_filter = data_filter

    def run(self, version: ProjectVersion):
        return [misuse for misuse in version.misuses if not self.data_filter.is_filtered(misuse.id)]
