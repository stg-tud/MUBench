from tempfile import mkdtemp
from os.path import join
from shutil import rmtree
from checkout import checkout
from checkout import checkout_parent
from datetime import datetime

def analyze(file, misuse):
    try:
        if "synthetic" in file:
            return ""
        
        fix = misuse["fix"]
        repository = fix["repository"]
        
        tmpdir = mkdtemp()
        misusedir = join(tmpdir, "misuse")
        fixdir = join(tmpdir, "fix")
        
        #checkout_parent(repository["type"], repository["url"], fix["revision"], misusedir, True)
        #checkout(repository["type"], repository["url"], fix["revision"], fixdir, True)
        
        # TODO: run actual analysis here
        result = ""

        try:
            rmtree(tmpdir)
        except PermissionError as e:
            print("Cleanup could not be completed for this repository: ")
            print(e)
        else:
            print("Cleanup successful")

        return result
    except Exception as e:
        # using str(e) would fail for unicode exceptions :/ 
        return "Error: {} in {}".format(repr(e), file)

import datareader
from pprint import pprint

start_time = datetime.now()
results = datareader.onAllDataDo(analyze, r'C:\Users\Mattis\Documents\Eko\MUBench\data', True)
end_time = datetime.now()

print("================================================")
print("Analysis finished! Total time: {}".format(str(end_time - start_time)))
print("Analysis results: ")
pprint(results)
print("================================================")
