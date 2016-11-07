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
            },
            "patterns": self.__get_patterns(misuse)
        })

        return self.ok()

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
        url = urljoin(self.review_site_url, METADATA_UPLOAD_PATH)
        post(url, self.__metadata)
