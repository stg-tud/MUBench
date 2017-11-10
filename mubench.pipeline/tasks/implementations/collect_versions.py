from data.project import Project
from utils.data_entity_lists import DataEntityLists


class CollectVersionsTask:
    def run(self, project: Project, data_entity_lists: DataEntityLists):
        return [version for version in project.versions
                if not self.__is_filtered(project.id, version.id, data_entity_lists)]

    @staticmethod
    def __is_filtered(project_id: str, version_id: str, data_entity_lists: DataEntityLists) -> bool:
        white_list = data_entity_lists.get_version_white_list(project_id)
        black_list = data_entity_lists.black_list

        is_whitelisted = not white_list or version_id in white_list
        is_blacklisted = version_id in black_list
        return is_blacklisted or not is_whitelisted
