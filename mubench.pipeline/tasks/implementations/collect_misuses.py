from data.project_version import ProjectVersion
from utils.data_filter import DataFilter


class CollectMisuses:
    # noinspection PyMethodMayBeStatic
    def run(self, data_filter: DataFilter, version: ProjectVersion):
        return [misuse for misuse in version.misuses if not data_filter.is_filtered(misuse.id)]
