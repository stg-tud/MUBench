import logging
from os.path import join

from data.misuse import Misuse
from data.project import Project
from data.project_version import ProjectVersion
from tasks.project_version_misuse_task import ProjectVersionMisuseTask


class Info(ProjectVersionMisuseTask):
    def __init__(self, checkouts_path, compiles_path):
        super().__init__()
        self.__logger = logging.getLogger("info")
        self.__checkouts_path = checkouts_path
        self.__compiles_path = compiles_path

    def process_project(self, project: Project):
        self.__logger.info("- Project    : %s", project.name)
        self.__logger.info("  Repository : %s:%s", project.repository.vcstype, project.repository.url)

        super().process_project(project)
    
    def process_project_version(self, project: Project, version: ProjectVersion):
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
        elif version_compile.needs_compile_patterns():
            compile_state = "project compiled, patterns not compiled"
        else:
            compile_state = "compiled"
        self.__logger.info("    Compile  : %s", compile_state)

        super().process_project_version(project, version)

        return self.ok()
    
    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse):
        self.__logger.info("    - Misuse           : %s", misuse.misuse_id)
        self.__logger.info("      Description      : %s", misuse.description.strip())
        self.__logger.info("      Fix Description  : %s", misuse.fix.description.strip())
        self.__logger.info("      Misuse Elements  : - %s", misuse.characteristics[0])
        for characteristic in misuse.characteristics[1:]:
            self.__logger.info("                         - %s", characteristic)

        checkout = version.get_checkout(self.__checkouts_path)
        if checkout.exists():
            location = misuse.location
            if project.repository.vcstype == "synthetic":
                checkout_path = join(version.path, "compile")
            else:
                checkout_path = checkout.checkout_dir
            source_file_path = join(checkout_path, version.source_dir, location.file)
            self.__logger.info("      Source File      : %s", source_file_path)
            self.__logger.info("      Enclosing Method : %s", location.method)

        self.__logger.info("      Fix Diff         : %s", misuse.fix.commit)

        return self.ok()
