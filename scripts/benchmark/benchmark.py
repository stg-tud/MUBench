import ntpath
from os import mkdir, getenv
from os.path import join, splitext
from shutil import rmtree
from subprocess import Popen
from tempfile import mkdtemp

from checkout import checkout, checkout_parent

DATA = r"<...>\MUBench\data"  # path to the data folder
DIR_BASE = r"<output_path>"  # used for saving intermediate results
MISUSE_DETECTOR = r"<path_to_jar>"  # path to the misuse detector to benchmark (must be an executable .jar)


def analyze(file, misuse):
    try:
        if "synthetic" in file:
            return "Warning: Ignored synthetic misuse " + file

        fix = misuse["fix"]
        repository = fix["repository"]

        dir_temp = mkdtemp()
        dir_misuse = join(dir_temp, "misuse")

        checkout_parent(repository["type"], repository["url"], fix["revision"], dir_misuse, True)

        # TODO: run actual analysis here (checked out misuse is in dir_misuse)
        result_dir = join(DIR_BASE, splitext(ntpath.basename(file))[0])
        print("Running \'{}\'; Results in \'{}\'...".format(MISUSE_DETECTOR, result_dir))
        p = Popen(["java", "-jar", MISUSE_DETECTOR, dir_misuse, result_dir], bufsize=1)
        p.wait()

        result = result_dir

        try:
            rmtree(dir_temp)
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
results = datareader.onAllDataDo(analyze, DATA, True)
end_time = datetime.now()

print("================================================")
print("Analysis finished! Total time: {}".format(str(end_time - start_time)))
print("Analysis results: ")
pprint(results)
print("================================================")
