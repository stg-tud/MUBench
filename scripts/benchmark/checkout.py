from os import listdir, makedirs
from os.path import join, isdir
from shutil import copy
from subprocess import Popen

import settings
from utils.io import safe_open


def get_parent(vcs: str, revision):
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


def checkout_parent(vcs: str, repository: str, revision, dir_target: str, verbose: bool) -> None:
    """
    Check out a repository on the parent of the given revision
    :type vcs: str
    :param vcs: the type of version control used by the repository
    :type repository: str
    :param repository: the repository url
    :type revision: str
    :param revision: the revision of which the parent will be checked out
    :type dir_target: str
    :param dir_target: the directory where the repository will be checked out in
    :type verbose: bool
    :param verbose: gives detailed console output
    :rtype None
    :return Returns nothing
    """

    checkout(vcs, repository, get_parent(vcs, revision), dir_target, verbose)


def checkout(vcs: str, repository: str, revision: str, dir_target: str, verbose: str) -> None:
    """
    Check out a repository on a certain revision
    :type vcs: str
    :param vcs: the type of version control used by the repository
    :type repository: str
    :param repository: the repository url
    :type revision: str
    :param revision: the revision to be checked out
    :type dir_target: str
    :param dir_target: the directory where the repository will be checked out in
    :type verbose: bool
    :param verbose: gives detailed console output
    :rtype None
    :return Returns nothing
    """

    if verbose:
        print("Checkout ({0}): ".format(vcs))
        print("Repository: " + repository)
        print("Revision: " + revision)
        print("Checking out into directory: " + dir_target)

    try:
        makedirs(dir_target, exist_ok=True)
    except FileExistsError as e:
        raise ValueError("{} is probably a file!".format(dir_target)) from e

    if isdir(dir_target) and (listdir(dir_target) == []):
        # Make sure no shell injection happens here!
        # For more detail go to https://docs.python.org/3/library/subprocess.html#security-considerations

        with safe_open(settings.LOG_FILE_CHECKOUT, 'a+') as log:
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
                svn_checkout = ['svn', 'checkout', '--revision', revision, repository]
                Popen(svn_checkout, cwd=dir_target, bufsize=1, stdout=log, stderr=log).wait()

            elif vcs == 'synthetic':
                copy(join(settings.DATA_PATH, repository), dir_target)

            else:
                raise ValueError("Unknown version control type: {}".format(vcs))
    else:
        raise ValueError("{0} is not an empty directory!".format(dir_target))


def reset_to_revision(vcs: str, local_repository: str, revision, verbose: bool):
    revision = str(revision)

    if verbose:
        print("Reset ({0}): ".format(vcs))
        print("Repository: " + local_repository)
        print("Revision: " + revision)

    with safe_open(settings.LOG_FILE_CHECKOUT, 'a+') as log:
        if vcs == 'git':
            Popen('git checkout ' + revision, cwd=local_repository, bufsize=1, shell=True, stdout=log, stderr=log).wait()
        elif vcs == 'svn':
            Popen('svn checkout --revision {}'.format(revision), cwd=local_repository, bufsize=1, stdout=log, stderr=log).wait()
        elif vcs == 'synthetic':
            pass  # nothing to do here
        else:
            raise ValueError("Unknown version control type: {}".format(vcs))
