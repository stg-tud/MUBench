import logging

from data.project import Project
from data.project_version import ProjectVersion
from utils.data_entity_lists import DataEntityLists


class CollectVersionsTask:
    def __init__(self, development_mode: bool):
        self._filter_non_compilable_versions = not development_mode

    def run(self, project: Project, data_entity_lists: DataEntityLists):
        versions = [version for version in project.versions
                    if not self.__is_filtered(project.id, version, data_entity_lists)]

        if not versions:
            logger = logging.getLogger("tasks.collect_versions")
            logger.warning("Filtered all versions of {}!".format(project))

        if self._filter_non_compilable_versions:
            versions = [version for version in versions if version.is_compilable]

        return versions

    @staticmethod
    def __is_filtered(project_id: str, version: ProjectVersion, data_entity_lists: DataEntityLists) -> bool:
        version_id = version.id
        white_list = data_entity_lists.get_version_white_list(project_id)
        black_list = data_entity_lists.black_list

        is_whitelisted = not white_list or version_id in white_list
        is_blacklisted = version_id in black_list

        return is_blacklisted or not is_whitelisted
