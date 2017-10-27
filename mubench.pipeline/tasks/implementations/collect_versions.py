from data.project import Project
from utils.data_entity_lists import DataEntityLists


class CollectVersionsTask:
    def __init__(self, data_entity_lists: DataEntityLists):
        self.version_white_list = data_entity_lists.version_white_list
        self.project_white_list = data_entity_lists.project_white_list
        self.black_list = data_entity_lists.black_list

    def run(self, project: Project):
        return [version for version in project.versions if not self.__is_filtered(project.id, version.id)]

    def __is_filtered(self, project_id: str, version_id: str) -> bool:
        white_list_is_empty = not self.project_white_list and not self.version_white_list
        is_whitelisted = white_list_is_empty or \
                         project_id in self.project_white_list or \
                         version_id in self.version_white_list
        is_blacklisted = version_id in self.black_list
        return is_blacklisted or not is_whitelisted
