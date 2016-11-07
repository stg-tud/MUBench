from typing import Dict
from typing import List
from urllib.parse import urljoin

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.tasks.project_misuse_task import ProjectMisuseTask
from benchmark.utils.web_util import post

METADATA_UPLOAD_PATH = "upload/metadata"


class PublishMetadataTask(ProjectMisuseTask):
    def __init__(self, review_site_url: str):
        super().__init__()
        self.review_site_url = review_site_url

        self.__metadata = []  # type: List[Dict]

    def start(self):
        self.__metadata.clear()

    def process_project_misuse(self, project: Project, misuse: Misuse):
        self.__metadata.append({
            "misuse": misuse.id,
            "location": misuse.location.__dict__,
            "description": misuse.description,
            "violation_types": misuse.characteristics,
            "fix": {
                "description": misuse.fix.description,
                "diff-url": misuse.fix.commit
            }
        })

        return self.ok()

    def end(self):
        url = urljoin(self.review_site_url, METADATA_UPLOAD_PATH)
        post(url, self.__metadata)
