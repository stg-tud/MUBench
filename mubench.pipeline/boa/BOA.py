import logging
import os
from os.path import exists
from typing import List

from utils import java_utils, io
from utils.shell import Shell


class GitProjectShallowCheckout:
    def __init__(self, name: str, url: str, base_path: str):
        self._logger = logging.getLogger("checkout.project")
        self.name = name
        self.url = url
        self.base_path = base_path
        self.path = os.path.join(base_path, name)

    def exists(self):
        return exists(self.path) and Shell.try_exec("git status", cwd=self.path, logger=self._logger)

    def clone(self):
        io.makedirs(self.path)
        clone_command = "git clone --depth 1 {} . --quiet -c core.askpass=true".format(self.url)
        Shell.exec(clone_command, cwd=self.path, logger=self._logger)

    def delete(self):
        io.remove_tree(self.path)

    def __str__(self):
        return "shallow-git:{}".format(self.url)


class GitHubProject:
    def __init__(self, project_id: str):
        self.id = project_id

    @property
    def repository_url(self):
        return "http://github.com/{}".format(self.id)

    def get_checkout(self, checkout_base_path: str) -> GitProjectShallowCheckout:
        return GitProjectShallowCheckout(self.id, self.repository_url, checkout_base_path)

    def __str__(self):
        return self.repository_url


class BOA:
    def __init__(self, username: str, password: str, results_path: str):
        self.username = username
        self.password = password
        self.results_path = results_path

    def query_projects_with_type_usages(self, types_names: List[str], subtypes_names: List[str]) -> List[GitHubProject]:
        projects = []
        query_id = "{}_{}".format("-".join(types_names), "-".join(subtypes_names))
        result_file_name = os.path.join(self.results_path, query_id + ".boaresult")
        if not os.path.exists(result_file_name):
            output = self.__try_query_projects_with_type_usages(subtypes_names)
            output_lines = output.splitlines()
            try:
                results_start_line = output_lines.index("Start output:") + 1
                results_end_line = output_lines.index("===")
                results = str.join(os.linesep, output_lines[results_start_line:results_end_line])
            except ValueError:
                # BOA returned no output
                results = ""

            os.makedirs(os.path.dirname(result_file_name), exist_ok=True)
            io.safe_write(results, result_file_name, append=False)

        with open(result_file_name, 'r') as result_file:
            for line in result_file.readlines():
                if line:
                    projects.append(GitHubProject(line[8:].strip()))

        return projects

    def __try_query_projects_with_type_usages(self, types_names: List, retry_count: int = 0):
        try:
            # SMELL manually escaping parameters
            return java_utils.exec_util("BOAExampleProjectFinder",
                                        "\"{}\" \"{}\" \"{}\"".format(self.username,
                                                                      self.password,
                                                                      ":".join(types_names)),
                                        timeout=20 * 60)
        except TimeoutError:
            # probably BOA stalled, retrying...
            if retry_count < 3:
                return self.__try_query_projects_with_type_usages(types_names, retry_count=retry_count + 1)
            else:
                return ""
