from os import listdir
from os.path import exists, join

from data.project import Project
from utils.data_entity_lists import DataEntityLists


class CollectProjectsTask:
    def __init__(self, data_path: str, data_entity_lists: DataEntityLists):
        self.data_path = data_path
        self.white_list = data_entity_lists.get_project_white_list()
        self.black_list = data_entity_lists.black_list

    def run(self):
        project_ids = []
        if exists(self.data_path):
            project_ids.extend(sorted(listdir(self.data_path)))

        return [Project(self.data_path, project_id) for project_id in project_ids if
                Project.is_project(join(self.data_path, project_id)) and not self.__is_filtered(project_id)]

    def __is_filtered(self, project_id: str) -> bool:
        is_whitelisted = not self.white_list or project_id in self.white_list
        is_blacklisted = project_id in self.black_list
        return is_blacklisted or not is_whitelisted
