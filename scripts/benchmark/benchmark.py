from genericpath import exists
from os import makedirs
from os.path import join, splitext, basename
from shutil import rmtree
from subprocess import Popen
from tempfile import mkdtemp

import settings
from checkout import checkout_parent
from results import evaluate_single_result


def analyze(file, misuse):
    try:
        if any([ignore in file for ignore in settings.IGNORES]):
            return "Warning: ignored {}".format(file)

        fix = misuse["fix"]
        repository = fix["repository"]

        dir_temp = mkdtemp()
        dir_misuse = join(dir_temp, settings.TEMP_SUBFOLDER)

        checkout_parent(repository["type"], repository["url"], fix["revision"], dir_misuse, True)

        result_dir = join(settings.RESULTS_PATH, splitext(basename(file))[0])
        print("Running \'{}\'; Results in \'{}\'...".format(settings.MISUSE_DETECTOR, result_dir))

        if not exists(result_dir):
            makedirs(result_dir)

        with open(join(result_dir, 'out.log'), 'w+') as log:
            p = Popen(["java", "-jar", settings.MISUSE_DETECTOR, dir_misuse, result_dir], bufsize=1,
                      stdout=log, stderr=log)
            p.wait()

        try:
            rmtree(dir_temp)
        except PermissionError as e:
            print("Cleanup could not be completed: ")
            print(e)
        else:
            print("Cleanup successful")

        return None

    except Exception as e:
        return "Error: {} in {}".format(str(e), file)
