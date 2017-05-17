import os
from typing import List

from data.project_checkout import GitProjectCheckout


class GitHubProject:
    def __init__(self, project_id: str):
        self.id = project_id

    @property
    def repository_url(self):
        return "http://github.com/{}".format(self.id)

    def get_checkout(self, checkout_base_path: str):
        return GitProjectCheckout(self.repository_url, checkout_base_path, self.id, "latest", "HEAD")

    def __str__(self):
        return self.id


class BOA:
    @staticmethod
    def query_projects_with_type_usages(type_name: str) -> List[GitHubProject]:
        result_file_name = os.path.join(os.path.dirname(__file__), "data", type_name + ".boaresult")
        if os.path.exists(result_file_name):
            projects = []
            with open(result_file_name, 'r') as result_file:
                for line in result_file.readlines():
                    projects.append(GitHubProject(line[8:].strip()))
            return projects
        else:
            raise UserWarning("no data for {}".format(type_name))
