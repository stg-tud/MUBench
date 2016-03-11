import sys
from os import listdir, mkdir
from os.path import join, exists, isdir
from subprocess import Popen

def checkout_parent(vctype, repository, revision, dirtarget, verbose):
    if (vctype == "git"):
        revision = revision + '~1'
    else:
        if (vctype == "svn"):
            revision = revision - 1
    
    checkout(vctype, repository, revision, dirtarget, verbose)

def checkout(vctype, repository, revision, dirtarget, verbose):
    revision = str(revision)

    if verbose:
        print("Checkout ({0}): ".format(vctype))
        print("Repository: " + repository)
        print("Revision: " + revision)
        print("Checking out into directory: " + dirtarget)
    
    if not exists(dirtarget):
        mkdir(dirtarget)
    
    if isdir(dirtarget) and (listdir(dirtarget)==[]):
        # Make sure no shell injection happens here!
        # For more detail go to https://docs.python.org/3/library/subprocess.html#security-considerations
        if (vctype == 'git'):
            command_clone = ['git', 'clone', repository, dirtarget]
            command_checkout = ['git', '--git-dir=' + join(dirtarget, '.git'), '--work-tree=' + dirtarget, 'checkout', revision]
            process_clone = Popen(command_clone, bufsize=1)
            process_checkout = Popen(command_checkout, bufsize=1)
            process_clone.wait()
            process_checkout.wait()
        else:
            if (vctype == 'svn'):
                command_checkout = ['svn', 'checkout', '--revision', str(revision), repository, dirtarget]
                process_checkout = Popen(command_checkout, bufsize=1)
                process_checkout.wait()
            else:
                raise ValueError('Unknown version control type: {}'.format(vctype))
    else:
        raise ValueError('{0} is not an empty directory!'.format(dirtarget))

# example usage (svn)
#from tempfile import mkdtemp
#svnrepository = 'svn://svn.code.sf.net/p/genoviz/code/trunk'
#revision = 4273
#checkout_parent("svn", svnrepository, revision, mkdtemp(suffix='_misuse'), True)
#checkout("svn", svnrepository, revision, mkdtemp(suffix='_fix'), True)

# example usage (git)
#from tempfile import mkdtemp
#gitrepository = r'https://github.com/haku/Onosendai.git'
#commit = '0e2a7570ab4491d0c4680ef52ee1008bef33fc02'
#checkout_parent("git", gitrepository, commit, mkdtemp(suffix='_misuse'), True)
#checkout("git", gitrepository, commit, mkdtemp(suffix='_fix'), True)
