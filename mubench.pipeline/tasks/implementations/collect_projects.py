from os import listdir
from os.path import exists, join

from data.project import Project


class CollectProjects:
    def __init__(self, data_path: str):
        self.data_path = data_path

    def run(self):
        project_ids = []
        if exists(self.data_path):
            project_ids.extend(sorted(listdir(self.data_path)))

        return [Project(self.data_path, project_id) for project_id in project_ids if
                Project.is_project(join(self.data_path, project_id))]
