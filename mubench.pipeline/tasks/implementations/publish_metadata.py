import getpass
import logging
import os
from typing import Dict
from typing import List
from urllib.parse import urljoin

from requests import RequestException

from data.misuse import Misuse
from data.project import Project
from data.snippets import SnippetUnavailableException
from utils.io import safe_read
from utils.web_util import post


class PublishMetadataTask:
    def __init__(self, checkouts_base_path: str,
                 review_site_url: str, review_site_user: str = "", review_site_password: str = ""):
        super().__init__()
        self.checkouts_base_path = checkouts_base_path
        self.review_site_url = review_site_url
        self.review_site_user = review_site_user
        self.review_site_password = review_site_password

        self.__metadata = []  # type: List[Dict]

        if self.review_site_user and not self.review_site_password:
            self.review_site_password = getpass.getpass(
                "Enter review-site password for '{}': ".format(self.review_site_user))

        self.__metadata.clear()

    def run(self, project: Project, misuse: Misuse):
        logger = logging.getLogger("tasks.publish_metadata")
        versions = [version for version in project.versions if misuse in version.misuses]
        if len(versions) == 1:
            version = versions[0]
        else:
            raise UserWarning("misuse {} is assigned to multiple project versions,"
                              " cannot handle this case!".format(misuse.id))

        self.__metadata.append({
            "project": project.id,
            "version": version.version_id,
            "misuse": misuse.misuse_id,
            "location": misuse.location.__dict__,
            "description": misuse.description,
            "violation_types": misuse.characteristics,
            "fix": {
                "description": misuse.fix.description,
                "diff-url": misuse.fix.commit
            },
            "target_snippets": [snippet.__dict__ for snippet in self.__get_snippets(misuse, version, logger)],
            "patterns": self.__get_patterns(misuse)
        })

    def __get_snippets(self, misuse, version, logger):
        checkout_base_path = version.get_checkout(self.checkouts_base_path).checkout_dir
        checkout_source_paths = [os.path.join(checkout_base_path, rel_path.lstrip(os.path.sep))
                                 for rel_path in version.source_dirs]
        try:
            return misuse.get_snippets(checkout_source_paths)
        except SnippetUnavailableException as e:
            logger.warn(e)
            return []

    def __get_patterns(self, misuse: Misuse):
        patterns = []
        for pattern in misuse.patterns:
            pattern_code_lines = safe_read(pattern.path).splitlines()
            pattern_code_lines = [line for line in pattern_code_lines if not self.__is_preamble_line(line)]
            pattern_code = "\n".join(pattern_code_lines)
            patterns.append({"id": pattern.name, "snippet": {"code": pattern_code, "first_line": 1}})
        return patterns

    @staticmethod
    def __is_preamble_line(line: str):
        return line.startswith("import") or line.startswith("package") or not line

    def end(self):
        url = urljoin(self.review_site_url, "metadata")
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
