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
        return self.repository_url


class BOA:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def query_projects_with_type_usages(self, type_name: str, subtype_name: str) -> List[GitHubProject]:
        projects = []
        query_id = "{}_{}".format(type_name, subtype_name)
        result_file_name = os.path.join(os.path.dirname(__file__), "results", query_id + ".boaresult")
        if not os.path.exists(result_file_name):
            output = self.__try_query_projects_with_type_usages(subtype_name)
            output_lines = output.splitlines()
            try:
                results_start_line = output_lines.index("Start output:") + 1
                results_end_line = output_lines.index("===")
                results = str.join(os.linesep, output_lines[results_start_line:results_end_line])
                io.safe_write(results, result_file_name, append=False)
            except ValueError:
                raise UserWarning("No output from BOA.")

        with open(result_file_name, 'r') as result_file:
            for line in result_file.readlines():
                if line:
                    projects.append(GitHubProject(line[8:].strip()))

        return projects

    def __try_query_projects_with_type_usages(self, type_name, retry_count: int = 0):
        try:
            # SMELL manually escaping parameters
            return java_utils.exec_util("BOAExampleProjectFinder",
                                        "\"{}\" \"{}\" \"{}\"".format(self.username, self.password, type_name),
                                        timeout=20 * 60)
        except TimeoutError:
            # probably BOA stalled, retrying...
            if retry_count < 3:
                return self.__try_query_projects_with_type_usages(type_name, retry_count=retry_count + 1)
            else:
                return ""
