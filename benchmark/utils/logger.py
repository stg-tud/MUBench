from config import Config
from utils.io import safe_write


def log_error(content: str) -> None:
    safe_write(content, Config.LOG_FILE_ERROR, True)
