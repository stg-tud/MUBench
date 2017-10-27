from typing import List


class DataEntityLists:
    def __init__(self, white_list: List[str], black_list: List[str]):
        self.__project_whitelist = DataEntityLists.__get_project_white_list(white_list)
        self.__version_whitelist = DataEntityLists.__get_version_white_list(white_list)
        self.__misuse_whitelist = DataEntityLists.__get_misuse_white_list(white_list)
        self.__black_list = black_list

    @property
    def project_white_list(self) -> List[str]:
        return self.__project_whitelist

    @property
    def version_white_list(self) -> List[str]:
        return self.__version_whitelist

    @property
    def misuse_white_list(self) -> List[str]:
        return self.__misuse_whitelist

    @property
    def black_list(self) -> List[str]:
        return self.__black_list

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
