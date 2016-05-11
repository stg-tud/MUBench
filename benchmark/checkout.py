import os
from os import makedirs
from os.path import join, exists, realpath, pardir, basename
from shutil import copy
from subprocess import Popen

from typing import Union, Dict

from benchmark.datareader import on_all_data_do
from benchmark.utils.data_util import extract_project_name_from_file_path
from benchmark.utils.io import safe_open
from benchmark.utils.printing import subprocess_print, print_ok


class Checkout:
    def __init__(self):
        self.data_path = realpath('data')
        self.checkout_base_dir = realpath('checkouts')

    @staticmethod
    def get_parent(vcs: str, revision: Union[int, str]) -> Union[str, int]:
        if vcs == 'git':
            return revision + '~1'
        elif vcs == 'svn':
            return int(revision) - 1
        elif vcs == 'synthetic':
            return revision
        else:
            raise ValueError("Unknown version control type: {}".format(vcs))

    def checkout_parent(self, vcs: str, repository: str, revision: str, dir_target: str) -> None:
        self.checkout(vcs, repository, self.get_parent(vcs, revision), dir_target)

    def checkout(self, vcs: str, repository: str, revision: str, dir_target: str) -> None:
        subprocess_print("Checkout - downloading project... ".format(vcs, repository, revision), end='')

        makedirs(dir_target, exist_ok=True)

        with safe_open(join(self.checkout_base_dir, "checkout.log"), 'a+') as log:
            if vcs == 'git':
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
                print("unknown vcs {}!".format(vcs))
                raise ValueError("Unknown version control type: {}".format(vcs))

        print_ok()

    def reset_to_revision(self, vcs: str, local_repository: str, revision: str):
        revision = str(revision)

        subprocess_print("Checkout - setting up correct revision... ", end='')

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
                print("unknown vcs {}!".format(vcs))
                raise ValueError("Unknown version control type: {}".format(vcs))

        print_ok()

    def single_checkout(self, file: str, misuse: Dict[str, str]) -> None:
        fix = misuse["fix"]
        repository = fix["repository"]

        project_name = extract_project_name_from_file_path(file)
        checkout_dir = join(self.checkout_base_dir, project_name)

        if not exists(checkout_dir):
            self.checkout(repository["type"], repository["url"], fix.get('revision', ""), checkout_dir)
        else:
            subprocess_print("Checkout - {} already checked out.".format(project_name))

    def do_all_checkouts(self) -> None:
        on_all_data_do(self.data_path, self.single_checkout, white_list=[""], black_list=[])
