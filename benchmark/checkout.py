import os
import subprocess
from os import makedirs
from os.path import join, exists, realpath
from shutil import copy
from typing import Union, Dict, Any

from benchmark.datareader import on_all_data_do
from benchmark.utils.data_util import extract_project_name_from_file_path
from benchmark.utils.io import safe_open
from benchmark.utils.printing import subprocess_print, print_ok


class Checkout:
    def __init__(self, checkout_parent: bool, setup_revisions: bool):
        self.data_path = realpath('data')
        self.checkout_base_dir = realpath('checkouts')
        self.checkout_parent = checkout_parent
        self.setup_revisions = setup_revisions

    def do_all_checkouts(self) -> None:
        on_all_data_do(self.data_path, self.checkout, white_list=[""], black_list=[])

    def checkout(self, file: str, misuse: Dict[str, Any]) -> bool:
        fix = misuse["fix"]
        repository = fix["repository"]
        vcs = repository["type"]
        revision = fix.get("revision", "")

        subprocess_print("Checkout ({}) - {} # {} : ", end='')

        if self.checkout_parent:
            revision = self.get_parent(vcs, revision)

        project_name = extract_project_name_from_file_path(file)
        checkout_dir = join(self.checkout_base_dir, project_name)

        if exists(checkout_dir):
            if not self.setup_revisions:
                print("already checked out.".format(project_name))
                return False
            reset_only = True
        else:
            reset_only = False
            makedirs(checkout_dir, exist_ok=True)

        print("running... ", end='')

        with safe_open(join(self.checkout_base_dir, "stdout.log"), 'a+') as outlog, \
                safe_open(join(self.checkout_base_dir, "stderr.log"), 'a+') as errlog:
            returncode = 0

            if vcs == 'git':
                if reset_only:
                    returncode += subprocess.call('git checkout ' + revision, cwd=checkout_dir, bufsize=1,
                                                  shell=True, stdout=outlog, stderr=errlog)
                else:
                    git_init = 'git init'
                    git_set_remote = 'git remote add origin ' + repository
                    git_fetch = 'git fetch'
                    git_checkout = 'git checkout ' + revision

                    returncode += subprocess.call(git_init, cwd=checkout_dir, bufsize=1, shell=True,
                                                  stdout=outlog, stderr=errlog)
                    returncode += subprocess.call(git_set_remote, cwd=checkout_dir, bufsize=1, shell=True,
                                                  stdout=outlog, stderr=errlog)
                    returncode += subprocess.call(git_fetch, cwd=checkout_dir, bufsize=1, shell=True,
                                                  stdout=outlog, stderr=errlog)
                    returncode += subprocess.call(git_checkout, cwd=checkout_dir, bufsize=1, shell=True,
                                                  stdout=outlog, stderr=errlog)
            elif vcs == 'svn':
                if reset_only:
                    svn_update = 'svn update -r {}'.format(revision)
                    returncode += subprocess.call(svn_update, cwd=checkout_dir, bufsize=1,
                                                  shell=True, stdout=outlog, stderr=errlog)
                else:
                    svn_checkout = 'svn checkout {}@{}'.format(repository, revision)
                    returncode += subprocess.call(svn_checkout, cwd=checkout_dir, bufsize=1, shell=True,
                                                  stdout=outlog, stderr=errlog)
            elif vcs == 'synthetic':
                if not reset_only:
                    copy(join(os.getcwd(), 'data', repository), checkout_dir)
            else:
                print("unknown vcs {}!".format(vcs))
                raise ValueError("Unknown version control type: {}".format(vcs))

        if returncode == 0:
            print_ok()
            return True
        else:
            print("error! (consider .log files in checkout subfolder for more detail)")
            return False

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
