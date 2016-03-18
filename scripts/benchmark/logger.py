import settings


def log(content: str):
    with open(settings.LOG_FILE, 'w+') as log_file:
        print(content, file=log_file)
