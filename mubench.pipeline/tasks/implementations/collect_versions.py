from data.project import Project
from utils.data_filter import DataFilter


class CollectVersionsTask:
    def __init__(self, data_filter: DataFilter):
        self.data_filter = data_filter

    def run(self, project: Project):
        return [version for version in project.versions if not self.data_filter.is_filtered(version.id)]
