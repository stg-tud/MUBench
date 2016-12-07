from nose.tools import assert_equals

from benchmark.data.finding import Finding
from benchmark.data.findings_filters import PotentialHits, AllFindings
from benchmark_tests.test_utils.data_util import create_misuse
from detectors.Dummy.Dummy import Dummy


class TestPotentialHits:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = Dummy("")
        self.misuse = create_misuse("-m1-")
        self.misuses = [self.misuse, create_misuse("-m2-")]

        self.uut = PotentialHits(self.detector, self.misuses)

    def test_adds_misuse(self):
        finding = Finding({})
        finding.is_potential_hit = lambda misuse, y: misuse == self.misuse

        potential_hits = self.uut.get_potential_hits([finding], "")

        assert_equals(self.misuse.id, potential_hits[0]["misuse"])


class TestAllFindings:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = Dummy("")

        self.misuse = create_misuse("-m1-")
        self.misuses = [self.misuse, create_misuse("-m2-")]

        self.uut = AllFindings(self.detector)

    def test_returns_all_findings(self):
        expected = [Finding({"id": "1", "file": ""}), Finding({"id": "2", "file": ""})]

        actual = self.uut.get_potential_hits(expected, "")

        assert_equals(expected, actual)

    def test_limits_number_of_findings(self):
        all = [Finding({"id": "1"}), Finding({"id": "2"})]
        self.uut.limit = 1

        actual = self.uut.get_potential_hits(all, "")

        assert_equals(1, len(actual))
