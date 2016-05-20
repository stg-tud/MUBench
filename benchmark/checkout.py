import subprocess
from os import makedirs, listdir
from os.path import join, exists, realpath
from shutil import copy

from typing import Union, Dict, Any

from benchmark import datareader
from benchmark.utils.data_util import extract_project_name_from_file_path
from benchmark.utils.printing import subprocess_print, print_ok


class Checkout:
    def __init__(self, checkout_parent: bool, setup_revisions: bool, outlog, errlog):
        self.data_path = realpath('data')
        self.checkout_base_dir = realpath('checkouts')
        self.checkout_parent = checkout_parent
        self.setup_revisions = setup_revisions
        self.outlog = outlog
        self.errlog = errlog

    def checkout(self, file: str, misuse: Dict[str, Any]) -> bool:
        fix = misuse["fix"]
        vcs = fix["repository"]["type"]
        revision = fix.get("revision", "")

        repository_url = fix["repository"]["url"]

        if self.checkout_parent:
            revision = self.get_parent(vcs, revision)

        project_name = extract_project_name_from_file_path(file)
        checkout_dir = join(self.checkout_base_dir, project_name)

        subprocess_print("Fetching ({}) from {}@{}: ".format(vcs, repository_url, revision), end='')

        if exists(checkout_dir) and listdir(checkout_dir):
            if not self.setup_revisions:
                print("already checked out.".format(project_name), flush=True)
                return False
            reset_only = True
        else:
            reset_only = False
            makedirs(checkout_dir, exist_ok=True)

        print("running... ", end='', flush=True)

        returncode = 0

        if vcs == 'git':
            if reset_only:
                returncode += subprocess.call('git checkout ' + revision, cwd=checkout_dir, bufsize=1,
                                              shell=True, stdout=self.outlog, stderr=self.errlog)
            else:
                git_init = 'git init'
                git_set_remote = 'git remote add origin ' + repository_url
                git_fetch = 'git fetch --quiet'
                git_checkout = 'git checkout {} --quiet'.format(revision)

                returncode += subprocess.call(git_init, cwd=checkout_dir, bufsize=1, shell=True,
                                              stdout=self.outlog, stderr=self.errlog)
                returncode += subprocess.call(git_set_remote, cwd=checkout_dir, bufsize=1, shell=True,
                                              stdout=self.outlog, stderr=self.errlog)
                returncode += subprocess.call(git_fetch, cwd=checkout_dir, bufsize=1, shell=True,
                                              stdout=self.outlog, stderr=self.errlog)
                returncode += subprocess.call(git_checkout, cwd=checkout_dir, bufsize=1, shell=True,
                                              stdout=self.outlog, stderr=self.errlog)
        elif vcs == 'svn':
            if reset_only:
                svn_update = 'svn update -r {}'.format(revision)
                returncode += subprocess.call(svn_update, cwd=checkout_dir, bufsize=1,
                                              shell=True, stdout=self.outlog, stderr=self.errlog)
            else:
                svn_checkout = 'svn checkout {}@{} .'.format(repository_url, revision)
                returncode += subprocess.call(svn_checkout, cwd=checkout_dir, bufsize=1, shell=True,
                                              stdout=self.outlog, stderr=self.errlog)
        elif vcs == 'synthetic':
            if not reset_only:
                copy(join('data', repository_url), checkout_dir)
        else:
            print("unknown vcs {}!".format(vcs), flush=True)
            raise ValueError("Unknown version control type: {}".format(vcs))

        if returncode == 0:
            print_ok()
        else:
            print("error! (consider .log files in checkout subfolder for more detail)", flush=True)
            raise datareader.Continue

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
