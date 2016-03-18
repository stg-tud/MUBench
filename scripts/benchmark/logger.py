from os import makedirs

from os.path import exists, join

import settings


def log(content: str):
    if not exists(settings.RESULTS_PATH):
        makedirs(settings.RESULTS_PATH)

    with open(join(settings.RESULTS_PATH, settings.LOG_FILE), 'w+') as log_file:
        print(content, file=log_file)
