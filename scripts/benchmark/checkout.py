from os import listdir, mkdir
from os.path import join, exists, isdir
from subprocess import Popen

from shutil import copy

from settings import DATA_PATH


def checkout_parent(vcs, repository, revision, dir_target, verbose):
    if vcs == 'git':
        revision += '~1'
    elif vcs == 'svn':
        revision -= 1
    elif vcs == 'synthetic':
        pass  # nothing to do

    checkout(vcs, repository, revision, dir_target, verbose)


def checkout(vcs, repository, revision, dir_target, verbose):
    revision = str(revision)

    if verbose:
        print("Checkout ({0}): ".format(vcs))
        print("Repository: " + repository)
        print("Revision: " + revision)
        print("Checking out into directory: " + dir_target)

    if not exists(dir_target):
        mkdir(dir_target)

    if isdir(dir_target) and (listdir(dir_target) == []):
        # Make sure no shell injection happens here!
        # For more detail go to https://docs.python.org/3/library/subprocess.html#security-considerations
        if vcs == 'git':
            # fetching is probably faster here than cloning
            cd = ['cd', dir_target]
            git_init = ['git', 'init']
            git_set_remote = ['git', 'remote', 'add', 'origin', repository]
            git_fetch = ['git', 'fetch']
            git_checkout = ['git', 'checkout', revision]
            sep = [';']

            command = cd + sep + git_init + sep + git_set_remote + sep + git_fetch + sep + git_checkout
            process = Popen(command, bufsize=1)
            process.wait()
        elif vcs == 'svn':
            command_checkout = ['svn', 'checkout', '--revision', str(revision), repository, dir_target]
            process_checkout = Popen(command_checkout, bufsize=1)
            process_checkout.wait()
        elif vcs == 'synthetic':
            copy(join(DATA_PATH, repository), dir_target)
        else:
            raise ValueError("Unknown version control type: {}".format(vcs))
    else:
        raise ValueError("{0} is not an empty directory!".format(dir_target))

# example usage (svn)
# from tempfile import mkdtemp
# svn_repository = 'svn://svn.code.sf.net/p/genoviz/code/trunk'
# revision = 4273
# checkout_parent("svn", svn_repository, revision, mkdtemp(suffix='_misuse'), True)
# checkout("svn", svn_repository, revision, mkdtemp(suffix='_fix'), True)

# example usage (git)
# from tempfile import mkdtemp
# git_repository = r'https://github.com/haku/Onosendai.git'
# commit = '0e2a7570ab4491d0c4680ef52ee1008bef33fc02'
# checkout_parent("git", git_repository, commit, mkdtemp(suffix='_misuse'), True)
# checkout("git", git_repository, commit, mkdtemp(suffix='_fix'), True)
