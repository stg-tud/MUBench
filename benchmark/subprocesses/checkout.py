import os
import subprocess
from distutils.dir_util import copy_tree
from os import makedirs, listdir
from os.path import join, exists, realpath
from shutil import rmtree

from typing import Union

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.io import safe_open
from benchmark.utils.printing import subprocess_print, print_ok


class Checkout(DataReaderSubprocess):
    def __init__(self, checkout_parent: bool, setup_revisions: bool, checkout_subdir: str, outlog: str, errlog: str):
        self.data_path = realpath('data')
        self.checkout_base_dir = realpath('checkouts')
        self.checkout_subdir = checkout_subdir
        self.checkout_parent = checkout_parent
        self.setup_revisions = setup_revisions
        self.outlog = outlog
        self.errlog = errlog

    def run(self, misuse: Misuse) -> bool:
        repository_url = misuse.repository.url
        vcs = misuse.repository.type
        revision = misuse.fix_revision

        if self.checkout_parent:
            revision = self.get_parent(vcs, revision)

        project_name = misuse.project_name
        project_dir = join(self.checkout_base_dir, project_name)
        checkout_dir = join(project_dir, self.checkout_subdir)

        subprocess_print("Fetching {}:{}#{}: ".format(vcs, repository_url, revision), end='')

        if self.__check_correct_checkout(vcs, checkout_dir):
            if not self.setup_revisions:
                print("already checked out.".format(project_name), flush=True)
                return False
            reset_only = True
        else:
            reset_only = False
            rmtree(checkout_dir, ignore_errors=True)
            makedirs(checkout_dir, exist_ok=True)

        print("running... ", end='', flush=True)

        returncode = 0

        with safe_open(join(project_dir, self.outlog), 'w+') as outlog, \
                safe_open(join(project_dir, self.errlog), 'w+') as errlog:
            if vcs == 'git':
                if not reset_only:
                    git_clone = 'git clone {} . --quiet'.format(repository_url)
                    returncode += subprocess.call(git_clone, cwd=checkout_dir, bufsize=1, shell=True,
                                                  stdout=outlog, stderr=errlog)

                git_checkout = 'git checkout {} --quiet'.format(revision)
                returncode += subprocess.call(git_checkout, cwd=checkout_dir, bufsize=1,
                                              shell=True, stdout=outlog, stderr=errlog)
            elif vcs == 'svn':
                if reset_only:
                    svn_update = 'svn update -r {}'.format(revision)
                    returncode += subprocess.call(svn_update, cwd=checkout_dir, bufsize=1,
                                                  shell=True, stdout=outlog, stderr=errlog)
                else:
                    svn_checkout = 'svn checkout {}@{} .'.format(repository_url, revision)
                    returncode += subprocess.call(svn_checkout, cwd=checkout_dir, bufsize=1, shell=True,
                                                  stdout=outlog, stderr=errlog)
            elif vcs == 'synthetic':
                rmtree(project_dir, ignore_errors=True)
                copy_tree(repository_url, checkout_dir)
            else:
                print("unknown vcs {}!".format(vcs), flush=True)
                return DataReaderSubprocess.Answer.skip

        if returncode == 0:
            print_ok()
            return DataReaderSubprocess.Answer.ok
        else:
            print("error! (consider .log files in checkout subfolder for more detail)", flush=True)
            return DataReaderSubprocess.Answer.skip

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

    @staticmethod
    def __check_correct_checkout(vcs: str, checkout_dir: str):
        if not exists(checkout_dir) or not listdir(checkout_dir):
            return False

        with open(os.devnull, 'w') as FNULL:
            if vcs == 'svn':
                returncode = subprocess.call('svn info', cwd=checkout_dir, bufsize=1, shell=True,
                                             stdout=FNULL, stderr=FNULL)
            elif vcs == 'git':
                returncode = subprocess.call('git status', cwd=checkout_dir, bufsize=1, shell=True,
                                             stdout=FNULL, stderr=FNULL)
            else:
                returncode = 0

        return returncode == 0
