import getpass
import logging
from typing import Dict
from typing import List
from urllib.parse import urljoin

from requests import RequestException

from data.misuse import Misuse
from data.project import Project
from tasks.project_misuse_task import ProjectMisuseTask
from utils.web_util import post


class PublishMetadataTask(ProjectMisuseTask):
    def __init__(self, compiles_base_path: str,
                 review_site_url: str, review_site_user: str="", review_site_password: str=""):
        super().__init__()
        self.compiles_base_path = compiles_base_path
        self.review_site_url = review_site_url
        self.review_site_user = review_site_user
        self.review_site_password = review_site_password

        self.__metadata = []  # type: List[Dict]

    def start(self):
        if self.review_site_user and not self.review_site_password:
            self.review_site_password = getpass.getpass(
                "Enter review-site password for '{}': ".format(self.review_site_user))

        self.__metadata.clear()

    def process_project_misuse(self, project: Project, misuse: Misuse):
        versions = [version for version in project.versions if misuse in version.misuses]
        if len(versions) == 1:
            version = versions[0]
        else:
            raise UserWarning("misuse {} is assigned to multiple project versions,"
                              " cannot handle this case!".format(misuse.id))

        self.__metadata.append({
            "project": project.id,
            "version": version.version_id,
            "misuse": misuse.id,
            "location": misuse.location.__dict__,
            "description": misuse.description,
            "violation_types": misuse.characteristics,
            "fix": {
                "description": misuse.fix.description,
                "diff-url": misuse.fix.commit
            },
            "target_snippets": self.__get_snippets(misuse, version),
            "patterns": self.__get_patterns(misuse)
        })

        return self.ok()

    def __get_snippets(self, misuse, version):
        version_compile = version.get_compile(self.compiles_base_path)
        return [snippet.__dict__ for snippet in misuse.get_snippets(version_compile.original_sources_path)]

    def __get_patterns(self, misuse: Misuse):
        patterns = []
        for pattern in misuse.patterns:
            with open(pattern.path, 'r') as pattern_file:
                pattern_code_lines = pattern_file.read().splitlines()
            pattern_code_lines = [line for line in pattern_code_lines if not self.__is_preamble_line(line)]
            pattern_code = "\n".join(pattern_code_lines)
            patterns.append({"id": pattern.name, "snippet": {"code": pattern_code, "first_line": 1}})
        return patterns

    @staticmethod
    def __is_preamble_line(line: str):
        return line.startswith("import") or line.startswith("package") or not line

    def end(self):
        url = urljoin(self.review_site_url, "api/upload/metadata")
        logger = logging.getLogger("publish.metadata")
        logger.info("Uploading metadata about %r misuses to %s...", len(self.__metadata), url)
        try:
            post(url, self.__metadata, username=self.review_site_user, password=self.review_site_password)
            logger.info("Metadata published.")
        except RequestException as e:
            response = e.response
            if response:
                logger.error("ERROR: %d %s: %s", response.status_code, response.reason, response.text)
            else:
                logger.error("ERROR: %s", e)
