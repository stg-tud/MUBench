from os import makedirs

from os.path import exists, join

import settings


def log_error(content: str):
    with open(join(settings.LOG_PATH, settings.LOG_FILE_ERROR), 'a+') as log_file:
        print(content, file=log_file)