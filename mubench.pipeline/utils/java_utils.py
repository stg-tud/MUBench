from os.path import dirname, join, exists

from os import remove
from urllib.error import URLError

from utils.shell import Shell
from utils.web_util import is_valid_file, download_file

UTILS_JAR_NAME = "mubench.utils.jar"
UTILS_JAR_URL = "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/{}".format(UTILS_JAR_NAME)
UTILS_MD5 = "6790ec09b26fd90df18409ccc59585e3"


def exec_util(main: str, args: str = ""):
    base_path = dirname(__file__)
    utils_jar_path = join(base_path, UTILS_JAR_NAME)

    if exists(utils_jar_path) and not is_valid_file(utils_jar_path, UTILS_MD5):
        remove(utils_jar_path)

    if not exists(utils_jar_path):
        try:
            download_file(UTILS_JAR_URL, utils_jar_path, UTILS_MD5)
        except (URLError, ValueError, FileNotFoundError) as e:
            raise ValueError("utils unavailable: {}".format(e))

    return Shell.exec("java -cp \"{}\" de.tu_darmstadt.stg.mubench.utils.{} {}".format(utils_jar_path, main, args))
