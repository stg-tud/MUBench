from typing import List

from data.filter_list import FilterList


class DataEntityLists:
    def __init__(self, white_list: List[str], black_list: List[str]):
        self.__project_whitelist = DataEntityLists.__get_project_white_list(white_list)
        self.__version_whitelist = DataEntityLists.__get_version_white_list(white_list)
        self.__misuse_whitelist = DataEntityLists.__get_misuse_white_list(white_list)
        self.__black_list = black_list

    def get_project_white_list(self) -> FilterList:
        return FilterList(self.__project_whitelist)

    def get_version_white_list(self, project_id: str) -> FilterList:
        return FilterList(
            (version_id for version_id in self.__version_whitelist if version_id.split('.')[0] == project_id))

    def get_misuse_white_list(self, version_id: str) -> FilterList:
        return FilterList(
            (misuse_id for misuse_id in self.__misuse_whitelist if misuse_id.rsplit('.', 1)[0] == version_id))

    @property
    def black_list(self) -> FilterList:
        return FilterList(self.__black_list)

    @staticmethod
    def __get_project_white_list(ids: List[str]) -> List[str]:
        return [id.partition('.')[0] for id in ids]

    @staticmethod
    def __get_version_white_list(ids: List[str]) -> List[str]:
        result = []
        for id in ids:
            split = id.split('.')
            if len(split) > 1:
                project_id = split[0]
                version_id = split[1]
                result.append("{}.{}".format(project_id, version_id))
        return result

    @staticmethod
    def __get_misuse_white_list(ids: List[str]) -> List[str]:
        return [id for id in ids if len(id.split('.')) > 2]
