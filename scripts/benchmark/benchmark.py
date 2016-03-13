from tempfile import mkdtemp
from os import mkdir, getenv
from os.path import join, splitext
import ntpath
from shutil import rmtree
from checkout import checkout, checkout_parent
from subprocess import Popen

def analyze(file, misuse):
    basepath=r"<output_path>"
    misuse_detector=r"<path_to_jar>"
    
    try:
        if "synthetic" in file:
            return "Warning: Ignored synthetic misuse " + file
        
        fix = misuse["fix"]
        repository = fix["repository"]
        
        tmpdir = mkdtemp()
        misusedir = join(tmpdir, "misuse")
        
        checkout_parent(repository["type"], repository["url"], fix["revision"], misusedir, True)
        
        # TODO: run actual analysis here (checked out misuse is in misusedir)
        resultdir = join(basepath, splitext(ntpath.basename(file))[0])
        print("Running \'{}\'; Results in \'{}\'...".format(misuse_detector, resultdir))
        p = Popen(["java", "-jar", misuse_detector, misusedir, resultdir], bufsize = 1) 
        p.wait()
        
        result = resultdir

        try:
            rmtree(tmpdir)
        except PermissionError as e:
            print("Cleanup could not be completed: ")
            print(e)
        else:
            print("Cleanup successful")

        return result
    
    except Exception as e:
        # using str(e) would fail for unicode exceptions :/ 
        return "Error: {} in {}".format(repr(e), file)

import datareader
from datetime import datetime
from pprint import pprint

start_time = datetime.now()
results = datareader.onAllDataDo(analyze, r'C:\Users\Mattis\Documents\Eko\MUBench\data', True)
end_time = datetime.now()

print("================================================")
print("Analysis finished! Total time: {}".format(str(end_time - start_time)))
print("Analysis results: ")
pprint(results)
print("================================================")
