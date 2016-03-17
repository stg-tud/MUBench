from os import listdir, mkdir
from os.path import join, exists, isdir
from subprocess import Popen

from shutil import copy

from settings import DATA_PATH


def checkout_parent(vcs: str, repository: str, revision, dir_target: str, verbose: bool) -> None:
    """
    Check out a repository on the parent of the given revision
    :param vcs: the type of version control used by the repository
    :param repository: the repository url
    :param revision: the revision of which the parent will be checked out
    :param dir_target: the directory where the repository will be checked out in
    :param verbose: gives detailed console output
    :return None
    """
    if vcs == 'git':
        revision += '~1'
    elif vcs == 'svn':
        revision -= 1
    elif vcs == 'synthetic':
        pass  # nothing to do

    checkout(vcs, repository, str(revision), dir_target, verbose)  # TODO test is str() is really needed here


def checkout(vcs: str, repository: str, revision: str, dir_target: str, verbose: str) -> None:
    """
    Check out a repository on a certain revision
    :param vcs: the type of version control used by the repository
    :param repository: the repository url
    :param revision: the revision to be checked out
    :param dir_target: the directory where the repository will be checked out in
    :param verbose: gives detailed console output
    :return None
    """
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
