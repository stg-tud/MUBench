from typing import Dict
from typing import List

from benchmark.data.finding import Finding
from benchmark.data.run import Run
from benchmark_tests.test_utils.data_util import create_misuse


class TestRun:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('misuse', meta={"location": {"file": "a", "method": "m()"}})

    def test_falls_back_to_method_name_if_no_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(p.A)"}])

    def test_matches_only_on_signature_if_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(A)"}, {"method": "method(B)"}])

    def assert_potential_hit(self, findings):
        run = Run("")
        run._Run__FINDINGS = self.create_findings(findings)
        assert run.get_potential_hits(self.misuse)

    def create_findings(self, findings_data: List[Dict[str, str]]):
        for finding in findings_data:
            if "file" not in finding:
                finding["file"] = self.misuse.location.file
            if "method" not in finding:
                finding["method"] = self.misuse.location.method

        return list(map(lambda data: Finding(data), findings_data))
