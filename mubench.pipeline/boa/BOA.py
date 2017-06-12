import os

from typing import List

from data.project_checkout import GitProjectCheckout
from utils import java_utils, io


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
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def query_projects_with_type_usages(self, type_name: str) -> List[GitHubProject]:
        projects = []
        result_file_name = os.path.join(os.path.dirname(__file__), "results", type_name + ".boaresult")
        if not os.path.exists(result_file_name):
            # SMELL manually escaping parameters
            output = java_utils.exec_util("BOAExampleProjectFinder",
                                          "\"{}\" \"{}\" \"{}\"".format(self.username, self.password, type_name))
            output_lines = output.splitlines()
            results_start_line = output_lines.find("Start output:") + 1
            results_end_line = output_lines.find("===")
            results = str.join(os.sep, output[results_start_line:results_end_line])
            io.safe_write(results, result_file_name, append=False)

        with open(result_file_name, 'r') as result_file:
            for line in result_file.readlines():
                projects.append(GitHubProject(line[8:].strip()))
        
        return projects
