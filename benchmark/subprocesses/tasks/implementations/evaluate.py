import yaml
from genericpath import exists, isfile, getsize
from os.path import join, basename, splitext
from typing import Dict, Optional, Iterable

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_misuse_task import ProjectVersionMisuseTask
from benchmark.utils.data_util import normalize_result_misuse_path
from benchmark.utils.dotgraph_util import get_labels
from benchmark.utils.io import safe_open
from benchmark.utils.printing import subprocess_print


class Evaluate(ProjectVersionMisuseTask):
    no_hit = 0
    potential_hit = 1

    def __init__(self, results_path: str, detector_result_file: str, checkout_base_dir: str, eval_result_file: str):
        super().__init__()
        self.results_path = results_path
        self.detector_result_file = detector_result_file
        self.checkout_base_dir = checkout_base_dir
        self.eval_result_file = eval_result_file

        self.results = []

    def process_project_version_misuse(self, project: Project, version: ProjectVersion, misuse: Misuse) -> Response:

        subprocess_print("Evaluation : running... ", end='')

        result_path = join(self.results_path, project.id, version.version_id)

        error_log = join(result_path, "error.log")
        errors_occurred = exists(error_log) and isfile(error_log) and getsize(error_log) > 0

        if not errors_occurred:
            with safe_open(join(result_path, "evaluation.log"), 'a+') as log:
                print("===========================================================", file=log)

                findings_file = join(result_path, self.detector_result_file)
                print("Evaluating result {}".format(findings_file), file=log)

                file_found = False
                label_found = False

                if exists(findings_file):
                    findings = yaml.load_all(safe_open(findings_file, 'r'))

                    src_prefix = version.source_dir

                    file_found = Evaluate.__is_file_found(findings, misuse,
                                                          join(self.checkout_base_dir, project.id),
                                                          src_prefix, log)
                    label_found = Evaluate.__is_label_found(findings, misuse, log)

                if file_found and label_found:
                    print("potential hit", flush=True)
                    self.results.append((misuse.id, Evaluate.potential_hit))
                    return Response.ok
                else:
                    print("no hit", flush=True)
                    self.results.append((misuse.id, Evaluate.no_hit))
                    return Response.ok

        print("ignored (no available findings)", flush=True)
        return Response.ok

    def teardown(self):
        self.output_results()

    def output_results(self) -> None:
        with safe_open(join(self.results_path, self.eval_result_file), 'w+') as file_result:
            for result in self.results:
                print(str(result).lstrip('(').rstrip(')'), file=file_result)

    @staticmethod
    def __is_file_found(findings: Iterable[Dict[str, str]], misuse: Misuse, checkout_dir: str,
                        src_prefix: Optional[str], log_stream) -> bool:

        for finding in findings:
            if finding is None:
                continue

            marked_file = finding.get("file")
            if marked_file is None:
                continue

            normed_finding = normalize_result_misuse_path(marked_file, checkout_dir, src_prefix)

            for pattern in misuse.patterns:
                # convert 'pattern123.java' back to 'pattern.java'
                finding_file_name, finding_file_extension = splitext(basename(normed_finding))
                finding_file_name = finding_file_name.rstrip('1234567890')

                if finding_file_name + finding_file_extension == pattern.file_name + pattern.file_extension:
                    return True

            misuse_file = misuse.location.file

            print("{}: Comparing found misuse {}".format(misuse_file, normed_finding),
                  file=log_stream)

            if normed_finding.endswith(misuse_file):
                print("Match found!", file=log_stream)
                return True
            else:
                print("No match", file=log_stream)

        return False

    @staticmethod
    def __is_label_found(findings: Iterable[Dict[str, str]], misuse: Misuse, log_stream) -> bool:

        marked_labels = []

        for finding in findings:
            if finding is None:
                continue
            graph = finding.get("graph")
            if graph is not None:
                marked_labels += get_labels(graph)

        if misuse is None:
            return True

        graph = misuse.usage

        expected_labels = get_labels(graph)

        # don't check if no labels are given on any end
        if not expected_labels or not marked_labels:
            return True

        for marked_label in marked_labels:
            is_expected_label = marked_label in expected_labels
            if is_expected_label:
                print("Found correct label!", file=log_stream)
                return True

        print("Correct label was not found!", file=log_stream)
        return False
