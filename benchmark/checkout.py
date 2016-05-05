import os
from os import listdir, makedirs
from os.path import join, isdir, exists, relpath, realpath, pardir
from shutil import copy
from subprocess import Popen
from typing import Union, Dict

from benchmark.datareader import on_all_data_do
from benchmark.utils.data_util import extract_project_name_from_file_path
from benchmark.utils.io import safe_open


class Checkout:
    def __init__(self, data_path: str, checkout_base_dir: str):
        self.data_path = data_path
        self.checkout_base_dir = checkout_base_dir

    @staticmethod
    def get_parent(vcs: str, revision: Union[int, str]) -> str:
        """
        Returns the parent of the given revision as a string
        :type vcs: str
        :param vcs: the type of version control the revision is from
        :param revision: the revision of which the parent will be returned (str for git ; int for svn)
        :rtype: str
        """
        if vcs == 'git':
            return str(revision + '~1')
        elif vcs == 'svn':
            return str(int(revision) - 1)
        elif vcs == 'synthetic':
            return str(revision)  # nothing to do
        else:
            raise ValueError("Unknown version control type: {}".format(vcs))

    @staticmethod
    def checkout_parent(vcs: str, repository: str, revision, dir_target: str) -> None:
        Checkout.checkout(vcs, repository, Checkout.get_parent(vcs, revision), dir_target)

    @staticmethod
    def checkout(vcs: str, repository: str, revision: str, dir_target: str) -> None:
        print("Checkout ({0}): ".format(vcs))
        print("Repository: " + repository)
        print("Revision: " + str(revision))
        print("Checking out into directory: " + dir_target)

        try:
            makedirs(dir_target, exist_ok=True)
        except FileExistsError as e:
            raise ValueError("{} is probably a file!".format(dir_target)) from e

        if isdir(dir_target) and (listdir(dir_target) == []):
            # Make sure no shell injection happens here!
            # For more detail go to https://docs.python.org/3/library/subprocess.html#security-considerations

            with safe_open(join(dir_target, "checkout.log"), 'a+') as log:
                print("================================================", file=log)
                print("Checkout({}): {}".format(vcs, repository), file=log)
                print("================================================", file=log)

                if vcs == 'git':
                    # fetching is probably faster here than cloning
                    git_init = 'git init'
                    git_set_remote = 'git remote add origin ' + repository
                    git_fetch = 'git fetch'
                    git_checkout = 'git checkout ' + revision

                    Popen(git_init, cwd=dir_target, bufsize=1, shell=True, stdout=log, stderr=log).wait()
                    Popen(git_set_remote, cwd=dir_target, bufsize=1, shell=True, stdout=log, stderr=log).wait()
                    Popen(git_fetch, cwd=dir_target, bufsize=1, shell=True, stdout=log, stderr=log).wait()
                    Popen(git_checkout, cwd=dir_target, bufsize=1, shell=True, stdout=log, stderr=log).wait()

                elif vcs == 'svn':
                    svn_checkout = ['svn', 'checkout', "{}@{}".format(repository, revision)]
                    Popen(svn_checkout, cwd=dir_target, bufsize=1, stdout=log, stderr=log).wait()

                elif vcs == 'synthetic':
                    copy(join(os.getcwd(), 'data', repository), dir_target)

                else:
                    raise ValueError("Unknown version control type: {}".format(vcs))
        else:
            raise ValueError("{0} is not an empty directory!".format(dir_target))

    @staticmethod
    def reset_to_revision(vcs: str, local_repository: str, revision: Union[str, int]):
        revision = str(revision)

        print("Reset ({0}): ".format(vcs))
        print("Repository: " + local_repository)
        print("Revision: " + revision)

        with safe_open(join(realpath(join(local_repository, pardir)), "checkout.log"), 'a+') as log:
            if vcs == 'git':
                Popen('git checkout ' + revision, cwd=local_repository, bufsize=1, shell=True, stdout=log,
                      stderr=log).wait()
            elif vcs == 'svn':
                Popen('svn update -r {}'.format(revision), cwd=local_repository, bufsize=1, shell=True, stdout=log,
                      stderr=log).wait()
            elif vcs == 'synthetic':
                pass  # nothing to do here
            else:
                raise ValueError("Unknown version control type: {}".format(vcs))

    def do_all_checkouts(self) -> None:
        def single_checkout(file: str, misuse: Dict[str, Union[str, Dict]]) -> None:
            fix = misuse["fix"]
            repository = fix["repository"]

            project_name = extract_project_name_from_file_path(file)
            checkout_dir = join(self.checkout_base_dir, project_name)

            if not exists(checkout_dir):
                self.checkout(repository["type"], repository["url"], fix.get('revision', ""), checkout_dir)
            else:
                print("{} is already checked out.".format(project_name))

        on_all_data_do(self.data_path, single_checkout, white_list=[""], black_list=[])
