import ntpath
from os.path import join, splitext
from shutil import rmtree
from subprocess import Popen
from tempfile import mkdtemp

from checkout import checkout_parent
from settings import *


def analyze(file, misuse):
    try:
        if "synthetic" in file:
            return "Warning: Ignored synthetic misuse " + file

        fix = misuse["fix"]
        repository = fix["repository"]

        dir_temp = mkdtemp()
        dir_misuse = join(dir_temp, TEMP_SUBFOLDER)

        checkout_parent(repository["type"], repository["url"], fix["revision"], dir_misuse, True)

        result_dir = join(RESULTS_PATH, splitext(ntpath.basename(file))[0])
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
