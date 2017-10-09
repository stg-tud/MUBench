from data.project import Project


class CollectVersions:
    # noinspection PyMethodMayBeStatic
    def run(self, project: Project):
        return project.versions
