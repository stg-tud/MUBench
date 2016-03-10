from os import listdir
from os import mkdir
from os.path import join
from os.path import exists
from os.path import isdir
from subprocess import CalledProcessError
from subprocess import check_output

class gitcheckout:
    def checkout_misuse(repository, fixing_commit, dirtarget, verbose):
        parent_of_fixing_commit = fixing_commit + '~1'
        
        if verbose:
            print("Checking out misuse to " + dirtarget)
            print("Repository: " + repository)
            print("Commit: " + parent_of_fixing_commit)
            
        gitcheckout.checkout(repository, parent_of_fixing_commit, dirtarget, verbose)
    
    def checkout_fix(repository, fixing_commit, dirtarget, verbose):
              
        if verbose:
            print("Checking out fix to " + dirtarget)
            print("Repository: " + repository)
            print("Commit: " + fixing_commit)
            
        gitcheckout.checkout(repository, fixing_commit, dirtarget, verbose)

    def checkout(repository, commit, dirtarget, verbose):
        try:
            if not exists(dirtarget):
                mkdir(dirtarget)
            
            if isdir(dirtarget) and (listdir(dirtarget)==[]):
                # Make sure no shell injection happens here!
                # For more detail go to https://docs.python.org/3/library/subprocess.html#security-considerations                
                check_output(['git', 'clone', repository, dirtarget], shell=True) 
                check_output(['git', '--git-dir=' + join(dirtarget, '.git'), '--work-tree=' + dirtarget, 'checkout', commit], shell=True)
            else:
                raise ValueError('{0} is an empty directory!'.format(dirtarget))
            
        except CalledProcessError as e:
            print("Git checkout failed: ")
            print(e)
            print(e.output.decode('unicode_escape'))
        except ValueError as e:
            print("Git checkout failed: ")
            print(e)
        else:
            if verbose:
                print("Git checkout successful.")

# example usage
from tempfile import mkdtemp
repository = r'https://github.com/google/closure-compiler'
commit = '67289ae4cbaba3ae70cd2e8fb92f3f2898039dfb'
gitcheckout.checkout_misuse(repository, commit, mkdtemp(suffix='_misuse'), True)
gitcheckout.checkout_fix(repository, commit, mkdtemp(suffix='_fix'), True)
