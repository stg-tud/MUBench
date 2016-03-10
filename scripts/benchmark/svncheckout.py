from os import listdir
from os import mkdir
from os.path import join
from os.path import exists
from os.path import isdir
from subprocess import CalledProcessError
from subprocess import check_output

class svncheckout:
    def checkout_misuse(repository, revision, dirtarget, verbose):
        revision = str(revision-1)

        if verbose:
            print("Checking out misuse to " + dirtarget)
            print("Repository: " + repository)
            print("Revision: " + revision)
            
        svncheckout.checkout(repository, revision, dirtarget, verbose)
        
    def checkout_fix(repository, revision, dirtarget, verbose):
        revision = str(revision)

        if verbose:
            print("Checking out fix to " + dirtarget)
            print("Repository: " + repository)
            print("Revision: " + revision)
            
        svncheckout.checkout(repository, revision, dirtarget, verbose)

    def checkout(repository, revision, dirtarget, verbose):
        try:
            if not exists(dirtarget):
                mkdir(dirtarget)
            
            if isdir(dirtarget) and (listdir(dirtarget)==[]):
                # Make sure no shell injection happens here!
                # For more detail go to https://docs.python.org/3/library/subprocess.html#security-considerations                
                check_output(['svn', 'checkout', '--revision', str(revision), repository, dirtarget], shell=True)
            else:
                raise ValueError('{0} is an empty directory!'.format(dirtarget))
            
        except CalledProcessError as e:
            print("SVN checkout failed: ")
            print(e)
            print(e.output.decode('unicode_escape'))
        except ValueError as e:
            print("SVN checkout failed: ")
            print(e)
        else:
            if verbose:
                print("SVN checkout successful.")

# example usage
from tempfile import mkdtemp
repository = 'svn://svn.code.sf.net/p/genoviz/code/trunk'
revision = 4273
svncheckout.checkout_misuse(repository, revision, mkdtemp(suffix='_misuse'), True)
svncheckout.checkout_fix(repository, revision, mkdtemp(suffix='_fix'), True) 
