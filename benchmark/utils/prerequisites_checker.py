import subprocess

from typing import Tuple

import config
from utils.io import safe_open


def check_prerequisites() -> Tuple[bool, str]:
    git_installed = check_git_installed()
    svn_installed = check_svn_installed()
    java_installed = check_java_installed()

    prerequisites_okay = git_installed and svn_installed and java_installed
    error_message = "Prerequisites okay!"

    if not prerequisites_okay:
        error_message = "ERROR! Missing Prerequisites: "

        if not git_installed:
            error_message += "Git, "
        if not svn_installed:
            error_message += "SVN, "
        if not java_installed:
            error_message += "Java"

    return prerequisites_okay, error_message


def check_git_installed() -> bool:

    try:
        with safe_open(config.__LOG_FILE_ERROR, 'w+') as error_log:
            subprocess.check_output(['git --version'], shell=True, stderr=error_log)
    except subprocess.CalledProcessError:
        return False

    return True


def check_svn_installed() -> bool:
    try:
        with safe_open(config.__LOG_FILE_ERROR, 'w+') as error_log:
            subprocess.check_output(['svn --version --quiet'], shell=True, stderr=error_log)
    except subprocess.CalledProcessError:
        return False

    return True


def check_java_installed() -> bool:
    try:
        with safe_open(config.__LOG_FILE_ERROR, 'w+') as error_log:
            subprocess.check_output(['java -version'], shell=True, stderr=error_log)
    except subprocess.CalledProcessError:
        return False

    return True
