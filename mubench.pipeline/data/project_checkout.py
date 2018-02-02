import logging
from os import listdir, makedirs
from os.path import join, exists
from zipfile import ZipFile

from utils.io import copy_tree, remove_tree, write_yaml, read_yaml
from utils.shell import Shell
from utils.web_util import download_file


class ProjectCheckout:
    __CHECKOUT_INFO_FILE = "checkout.yml"
    __KEY_TIMESTAMP = "timestamp"
    __DEFAULT_TIMESTAMP = 0

    def __init__(self, url: str, base_path: str, name: str):
        self._logger = logging.getLogger("checkout.project")
        self.url = url
        self.base_path = base_path
        self.name = name
        self.checkout_dir = join(self.base_path, name, "checkout")
        self._checkout_info_file = join(self.checkout_dir, ProjectCheckout.__CHECKOUT_INFO_FILE)

    @property
    def timestamp(self) -> int:
        timestamp = self.__DEFAULT_TIMESTAMP

        if exists(self._checkout_info_file):
            checkout_info = read_yaml(self._checkout_info_file)
            timestamp = checkout_info.get(ProjectCheckout.__KEY_TIMESTAMP, self.__DEFAULT_TIMESTAMP)

        return timestamp

    def exists(self) -> bool:
        raise NotImplementedError

    def create(self, current_timestamp: int) -> None:
        self._create()
        checkout_info = {ProjectCheckout.__KEY_TIMESTAMP: current_timestamp}
        write_yaml(checkout_info, self._checkout_info_file)

    def _create(self):
        raise NotImplementedError

    def delete(self) -> None:
        raise NotImplementedError


class LocalProjectCheckout(ProjectCheckout):
    def exists(self):
        return exists(self.checkout_dir) and listdir(self.checkout_dir)

    def _create(self):
        if not exists(self.checkout_dir):
            self._logger.debug("Create checkout directory %s", self.checkout_dir)
            makedirs(self.checkout_dir)
        if not listdir(self.checkout_dir):
            self._logger.debug("Copy from %s", self.url)
            copy_tree(self.url, self.checkout_dir)

    def delete(self):
        self._logger.debug("Delete %s", self.checkout_dir)
        remove_tree(self.checkout_dir)

    def __str__(self):
        return "local:{}".format(self.url)


class SyntheticProjectCheckout(ProjectCheckout):
    def __init__(self, name: str, version: str, data_path: str, base_path: str):
        super().__init__("-synthetic-", join(base_path, name), version)
        self.name = name
        self.version = version
        self.data_path = data_path

    def exists(self) -> bool:
        return exists(self.checkout_dir)

    def delete(self) -> None:
        self._logger.debug("Delete %s", self.checkout_dir)
        remove_tree(self.checkout_dir)

    def _create(self) -> None:
        if not exists(self.checkout_dir):
            self._logger.debug("Create checkout directory %s", self.checkout_dir)
            makedirs(self.checkout_dir)
            copy_tree(join(self.data_path, "repo"), self.checkout_dir)

    def __str__(self):
        return "synthetic:{}.{}".format(self.name, self.version)


class ZipProjectCheckout(ProjectCheckout):
    def __init__(self, name: str, version: str, revision_url: str, md5_checksum: str, base_path: str):
        super().__init__(revision_url, base_path, name)
        self.md5_checksum = md5_checksum
        self.version = version
        self.__base_checkout_dir = self.checkout_dir
        self.__child = LocalProjectCheckout(self.checkout_dir, join(self.base_path, self.name), self.version)
        self.checkout_dir = self.__child.checkout_dir

    def delete(self) -> None:
        remove_tree(self.checkout_dir)

    def _create(self) -> None:
        makedirs(self.checkout_dir, exist_ok=True)
        bundle_file = join(self.checkout_dir, "bundle.zip")
        download_file(self.url, bundle_file, self.md5_checksum)
        with ZipFile(bundle_file) as zip_file:
            zip_file.extractall(self.checkout_dir)

    def exists(self) -> bool:
        return exists(self.checkout_dir) and len(listdir(self.checkout_dir)) > 1

    def __str__(self):
        return "zip:{}:{}".format(self.name, self.url)


class RepoProjectCheckout(ProjectCheckout):
    def __init__(self, name: str, version: str, url: str, revision: str, base_path: str):
        super(RepoProjectCheckout, self).__init__(url, base_path, name)
        self.version = version
        self.revision = revision
        self.__base_checkout_dir = self.checkout_dir
        self.__child = LocalProjectCheckout(self.checkout_dir, join(self.base_path, self.name), self.version)
        self.checkout_dir = self.__child.checkout_dir

    def exists(self):
        return self.__child.exists() and self._is_repo(self.checkout_dir)

    def _create(self):
        if not self._is_repo(self.__base_checkout_dir):
            self._logger.debug("Create base checkout directory %s", self.__base_checkout_dir)
            makedirs(self.__base_checkout_dir, exist_ok=True)
            self._logger.debug("Clone from %s", self)
            self._clone(self.url, self.revision, self.__base_checkout_dir)

        if not self._is_repo(self.__child.checkout_dir):
            self.__child._create()
            self._logger.debug("Update to revision %s", self.revision)
            self._update(self.url, self.revision, self.__child.checkout_dir)

    def delete(self):
        self._logger.debug("Delete %s", self.__base_checkout_dir)
        remove_tree(self.__base_checkout_dir)
        self.__child.delete()

    def _clone(self, url: str, revision: str, path: str):
        raise NotImplementedError

    def _update(self, url: str, revision: str, path: str):
        raise NotImplementedError

    def _is_repo(self, path: str) -> bool:
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class GitProjectCheckout(RepoProjectCheckout):
    def _clone(self, url: str, revision: str, path: str):
        Shell.exec("git clone {} . --quiet".format(url), cwd=path, logger=self._logger)

    def _update(self, url: str, revision: str, path: str):
        Shell.exec("git checkout {} --quiet".format(revision), cwd=path, logger=self._logger)

    def _is_repo(self, path: str):
        return exists(path) and Shell.try_exec("git status", cwd=path, logger=self._logger)

    def __str__(self):
        return "git:{}#{}".format(self.url, self.revision[:8])


class SVNProjectCheckout(ProjectCheckout):
    def __init__(self, name: str, version: str, url: str, revision: str, base_path: str):
        super().__init__(url, base_path, name)
        self.version = version
        self.revision = revision
        self.__base_checkout_dir = self.checkout_dir
        self.checkout_dir = join(self.base_path, name, version, "checkout")

    def _create(self) -> None:
        self._logger.debug("Create checkout directory %s", self.checkout_dir)
        makedirs(self.checkout_dir, exist_ok=True)
        self._logger.debug("Checkout from %s", self.url)
        Shell.exec("svn checkout \"{}@{}\" .".format(self.url, self.revision), cwd=self.checkout_dir)
        Shell.exec("svn upgrade", cwd=self.checkout_dir)

    def exists(self) -> bool:
        return exists(self.checkout_dir) and Shell.try_exec("svn info", cwd=self.checkout_dir)

    def delete(self) -> None:
        self._logger.debug("Delete %s", self.__base_checkout_dir)
        remove_tree(self.checkout_dir)

    def __str__(self):
        return "svn:{}@{}".format(self.url, self.revision)
