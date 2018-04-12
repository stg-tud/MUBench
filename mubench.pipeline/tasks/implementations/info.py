import logging

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion


class ProjectInfoTask:
    def __init__(self, checkouts_path, compiles_path):
        self.__logger = logging.getLogger("info.project")
        self.__checkouts_path = checkouts_path
        self.__compiles_path = compiles_path

    def run(self, project: Project):
        self.__logger.info("- Project    : %s", project.name)
        self.__logger.info("  Repository : %s:%s", project.repository.vcstype, project.repository.url)


class VersionInfoTask:
    def __init__(self, checkouts_path, compiles_path):
        self.__logger = logging.getLogger("info.version")
        self.__checkouts_path = checkouts_path
        self.__compiles_path = compiles_path

    def run(self, project: Project, version: ProjectVersion):
        self.__logger.info("  - Version  : %s", version.version_id)
        revision = "-"
        if project.repository.vcstype == "git":
            revision = version.revision + "~1"
        elif project.repository.vcstype == "svn":
            revision = str(int(version.revision) - 1)
        self.__logger.info("    Revision : %s", revision)

        checkout = version.get_checkout(self.__checkouts_path)
        if not checkout.exists():
            self.__logger.info("    Checkout : not checked out")
        else:
            self.__logger.info("    Checkout : %s", checkout.checkout_dir)

        version_compile = version.get_compile(self.__compiles_path)
        if version_compile.needs_compile():
            compile_state = "not compiled"
        else:
            compile_state = "compiled"
        self.__logger.info("    Compile  : %s", compile_state)


class MisuseInfoTask:
    def __init__(self, checkouts_path, compiles_path):
        self.__logger = logging.getLogger("info.misuse")
        self.__checkouts_path = checkouts_path
        self.__compiles_path = compiles_path

    def run(self, misuse: Misuse):
        self.__logger.info("    - Misuse           : %s", misuse.misuse_id)
        self.__logger.info("      Description      : %s", misuse.description.strip())
        self.__logger.info("      Fix Description  : %s", misuse.fix.description.strip())
        self.__logger.info("      Misuse Elements  : - %s", misuse.violations[0])
        for violation in misuse.violations[1:]:
            self.__logger.info("                         - %s", violation)

        self.__logger.info("      Fix Diff         : %s", misuse.fix.commit)
