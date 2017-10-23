from os import listdir
from os.path import exists, join

from data.project import Project
from utils.data_filter import DataFilter


class CollectProjectsTask:
    def __init__(self, data_path: str, data_filter: DataFilter):
        self.data_path = data_path
        self.data_filter = data_filter

    def run(self):
        project_ids = []
        if exists(self.data_path):
            project_ids.extend(sorted(listdir(self.data_path)))

        return [Project(self.data_path, project_id) for project_id in project_ids if
                Project.is_project(join(self.data_path, project_id)) and not self.data_filter.is_filtered(project_id)]
