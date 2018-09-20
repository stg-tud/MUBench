from os import remove
from os.path import dirname, join, exists
from typing import Optional
from urllib.error import URLError

from utils.shell import Shell
from utils.web_util import is_valid_file, download_file

__UTILS_VERSION = "0.0.4"
__UTILS_JAR_NAME = "mubench.utils-{}-jar-with-dependencies.jar".format(__UTILS_VERSION)
__UTILS_JAR_URL = "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/" \
                  "de/tu-darmstadt/stg/mubench/mubench.utils/{}/{}".format(__UTILS_VERSION, __UTILS_JAR_NAME)
__UTILS_JAR_MD5 = "610c4b72c2bb89865d9bf756c0980862"


def exec_util(main: str, args: str = "", timeout: Optional[int] = None):
    base_path = dirname(__file__)
    utils_jar_path = join(base_path, __UTILS_JAR_NAME)

    if exists(utils_jar_path) and not is_valid_file(utils_jar_path, __UTILS_JAR_MD5):
        remove(utils_jar_path)

    if not exists(utils_jar_path):
        try:
            download_file(__UTILS_JAR_URL, utils_jar_path, __UTILS_JAR_MD5)
        except (URLError, ValueError, FileNotFoundError) as e:
            raise ValueError("utils unavailable: {}".format(e))

    return Shell.exec("java -cp \"{}\" de.tu_darmstadt.stg.mubench.utils.{} {}".format(utils_jar_path, main, args),
                      timeout=timeout)
