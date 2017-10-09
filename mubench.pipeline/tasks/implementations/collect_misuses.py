from data.project_version import ProjectVersion


class CollectMisuses:
    # noinspection PyMethodMayBeStatic
    def run(self, version: ProjectVersion):
        return version.misuses
