import sys
import subprocess
from subprocess import CalledProcessError
from subprocess import check_output
from os.path import join
from os.path import dirname
from os.path import realpath

class gitCheckout:
    def checkoutMisuse(self, fixing_commit, dirtarget, verbose):
        repository, unused, commit_hash = fixing_commit.rsplit('/', 2)
        commit_hash += "^1"
        
        if verbose:
            print("Checking out misuse to " + dirtarget)
            print("Repository: " + repository)
            print("Commit hash: " + commit_hash)
            
        gitCheckout().checkout(repository, commit_hash, dirtarget)
        
    def checkoutFix(self, fixing_commit, dirtarget, verbose):
        repository, unused, commit_hash = fixing_commit.rsplit('/', 2)
        
        if verbose:
            print("Checking out fix to " + dirtarget)
            print("Repository: " + repository)
            print("Commit hash: " + commit_hash)
            
        gitCheckout().checkout(repository, commit_hash, dirtarget)

    def checkout(self, repository, commit_hash, dirtarget):
        try:
            gitcheckout = join(dirname(realpath(__file__)), 'gitcheckout.sh')
            check_output([gitcheckout, repository, commit_hash, dirtarget],
            executable=gitcheckout, stderr=subprocess.STDOUT)
        except CalledProcessError as e:
            print("Git checkout failed: ")
            print(e.output.decode('unicode_escape'))
        else:
            print("Git checkout successful.")

# example usage
from tempfile import mkdtemp
commitid = 'https://github.com/google/closure-compiler/commit/67289ae4cbaba3ae70cd2e8fb92f3f2898039dfb'
gitCheckout().checkoutMisuse(commitid, mkdtemp(suffix='_misuse'), True)
gitCheckout().checkoutFix(commitid, mkdtemp(suffix='_fix'), True) 
