from data.project_version import ProjectVersion
from utils.data_entity_lists import DataEntityLists


class CollectMisusesTask:
    def __init__(self, data_entity_lists: DataEntityLists):
        self.data_entity_lists = data_entity_lists

    def run(self, version: ProjectVersion):
        return [misuse for misuse in version.misuses if not self.__is_filtered(version.id, misuse.id)]

    def __is_filtered(self, version_id: str, misuse_id: str) -> bool:
        white_list = self.data_entity_lists.get_misuse_white_list(version_id)
        is_whitelisted = not white_list or misuse_id in white_list
        is_blacklisted = misuse_id in self.data_entity_lists.black_list
        return is_blacklisted or not is_whitelisted
