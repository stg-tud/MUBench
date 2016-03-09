import sys
import subprocess
from subprocess import CalledProcessError
from subprocess import check_output
from os.path import join
from os.path import dirname
from os.path import realpath

class svnCheckout:
    def checkoutMisuse(self, fixing_commit, dirtarget, verbose):
        repository, revision = '' #TODO
        
        if verbose:
            print("Checking out misuse to " + dirtarget)
            print("Repository: " + repository)
            print("Revision: " + revision)
            
        svnCheckout().checkout(repository, revision, dirtarget)
        
    def checkoutFix(self, fixing_commit, dirtarget, verbose):
        repository, revision = '' #TODO
        
        if verbose:
            print("Checking out fix to " + dirtarget)
            print("Repository: " + repository)
            print("Revision: " + revision)
            
        svnCheckout().checkout(repository, commit_hash, dirtarget)

    def checkout(self, repository, revision, dirtarget):
        try:
            svncheckout = join(dirname(realpath(__file__)), 'svncheckout.sh')
            check_output([svncheckout, repository, revision, dirtarget],
            executable=svncheckout, stderr=subprocess.STDOUT)
        except CalledProcessError as e:
            print("SVN checkout failed: ")
            print(e.output.decode('unicode_escape'))
        else:
            print("SVN checkout successful.")

# example usage
from tempfile import mkdtemp
revision_url = ''
svnCheckout().checkoutMisuse(revision_url, mkdtemp(suffix='_misuse'), True)
svnCheckout().checkoutFix(revision_url, mkdtemp(suffix='_fix'), True) 
