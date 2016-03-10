import sys
from os import listdir
from os import mkdir
from os.path import join
from os.path import exists
from os.path import isdir
from subprocess import check_output

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
            check_output(['git', 'clone', repository, dirtarget], shell=True) 
            check_output(['git', '--git-dir=' + join(dirtarget, '.git'), '--work-tree=' + dirtarget, 'checkout', revision], stdout=STDOUT, shell=True)
        else:
            if (vctype == 'svn'): 
                check_output(['svn', 'checkout', '--revision', str(revision), repository, dirtarget], shell=True)
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
#gitrepository = r'https://github.com/haku/Onosendai.git'
#commit = '0e2a7570ab4491d0c4680ef52ee1008bef33fc02'
#checkout_parent("git", gitrepository, commit, mkdtemp(suffix='_misuse'), True)
#checkout("git", gitrepository, commit, mkdtemp(suffix='_fix'), True)
