from os import listdir
from os.path import exists, join

from data.project import Project
from utils.data_entity_lists import DataEntityLists


class CollectProjectsTask:
    def __init__(self, data_path: str):
        self.data_path = data_path

    def run(self, data_entity_lists: DataEntityLists):
        project_ids = []
        if exists(self.data_path):
            project_ids.extend(sorted(listdir(self.data_path)))

        return [Project(self.data_path, project_id) for project_id in project_ids if
                Project.is_project(join(self.data_path, project_id)) and
                not self.__is_filtered(project_id, data_entity_lists)]

    @staticmethod
    def __is_filtered(project_id: str, data_entity_lists: DataEntityLists) -> bool:
        white_list = data_entity_lists.get_project_white_list()
        black_list = data_entity_lists.black_list

        is_whitelisted = not white_list or white_list.case_insensitive_contains(project_id)
        is_blacklisted = black_list.case_insensitive_contains(project_id)
        return is_blacklisted or not is_whitelisted
