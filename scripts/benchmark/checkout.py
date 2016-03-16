from os import listdir, mkdir
from os.path import join, exists, isdir
from subprocess import Popen


def checkout_parent(vcs, repository, revision, dir_target, verbose):
    if vcs == "git":
        revision += '~1'
    else:
        if vcs == "svn":
            revision -= 1

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
            command_clone = ['git', 'clone', repository, dir_target]
            command_checkout = ['git', '--git-dir=' + join(dir_target, '.git'), '--work-tree=' + dir_target, 'checkout',
                                revision]
            process_clone = Popen(command_clone, bufsize=1)
            process_checkout = Popen(command_checkout, bufsize=1)
            process_clone.wait()
            process_checkout.wait()
        else:
            if vcs == 'svn':
                command_checkout = ['svn', 'checkout', '--revision', str(revision), repository, dir_target]
                process_checkout = Popen(command_checkout, bufsize=1)
                process_checkout.wait()
            else:
                raise ValueError('Unknown version control type: {}'.format(vcs))
    else:
        raise ValueError('{0} is not an empty directory!'.format(dir_target))

# example usage (svn)
# from tempfile import mkdtemp
# svnrepository = 'svn://svn.code.sf.net/p/genoviz/code/trunk'
# revision = 4273
# checkout_parent("svn", svnrepository, revision, mkdtemp(suffix='_misuse'), True)
# checkout("svn", svnrepository, revision, mkdtemp(suffix='_fix'), True)

# example usage (git)
# from tempfile import mkdtemp
# gitrepository = r'https://github.com/haku/Onosendai.git'
# commit = '0e2a7570ab4491d0c4680ef52ee1008bef33fc02'
# checkout_parent("git", gitrepository, commit, mkdtemp(suffix='_misuse'), True)
# checkout("git", gitrepository, commit, mkdtemp(suffix='_fix'), True)
