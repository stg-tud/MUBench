import subprocess
from os import linesep
from typing import Tuple

import settings
from utils.io import safe_open


def check_prerequisites() -> Tuple[bool, str]:
    git_installed, git_error = check_git_installed()
    svn_installed, svn_error = check_svn_installed()
    java_installed, java_error = check_java_installed()

    prerequisites_okay = git_installed and svn_installed and java_installed

    error_message = "Missing prerequisites:" + linesep
    error_message = error_message + git_error + svn_error + java_error

    return prerequisites_okay, error_message


def check_git_installed() -> Tuple[bool, str]:

    try:
        with safe_open(settings.LOG_FILE_ERROR, 'w+') as error_log:
            subprocess.check_output(['git', '--version'], stderr=error_log)
    except subprocess.CalledProcessError as error:
        return False, "Git:" + linesep + error.output + linesep

    return True, ""


def check_svn_installed() -> Tuple[bool, str]:
    try:
        with safe_open(settings.LOG_FILE_ERROR, 'w+') as error_log:
            subprocess.check_output(['svn', '--version', '--quiet'], stderr=error_log)
    except subprocess.CalledProcessError as error:
        return False, "SVN:" + linesep + error.output + linesep

    return True, ""


def check_java_installed() -> Tuple[bool, str]:
    try:
        with safe_open(settings.LOG_FILE_ERROR, 'w+') as error_log:
            subprocess.check_output(['java', '-version'], stderr=error_log)
    except subprocess.CalledProcessError as error:
        return False, "Java:" + linesep + error.output + linesep

    return True, ""
