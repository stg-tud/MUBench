from os import makedirs

from os.path import exists, join

import settings


def log_error(content: str):
    create_log_path()
    with open(join(settings.LOG_PATH, settings.LOG_FILE_ERROR), 'w+') as log_file:
        print(content, file=log_file)


def create_log_path():
    if not exists(settings.LOG_PATH):
        makedirs(settings.LOG_PATH)
