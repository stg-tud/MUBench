from data.project import Project
from utils.data_entity_lists import DataEntityLists


class CollectVersionsTask:
    def __init__(self, data_entity_lists: DataEntityLists):
        self.data_entity_lists = data_entity_lists
        self.black_list = data_entity_lists.black_list

    def run(self, project: Project):
        return [version for version in project.versions if not self.__is_filtered(project.id, version.id)]

    def __is_filtered(self, project_id: str, version_id: str) -> bool:
        white_list = self.data_entity_lists.get_version_white_list(project_id)
        is_whitelisted = not white_list or version_id in white_list
        is_blacklisted = version_id in self.black_list
        return is_blacklisted or not is_whitelisted
