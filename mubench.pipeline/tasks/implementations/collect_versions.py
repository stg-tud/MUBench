from data.project import Project
from utils.data_filter import DataFilter


class CollectVersions:
    # noinspection PyMethodMayBeStatic
    def run(self, data_filter: DataFilter, project: Project):
        return [version for version in project.versions if not data_filter.is_filtered(version.id)]
