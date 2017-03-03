from nose.tools import assert_equals

from data.finding import Finding
from data.findings_filters import PotentialHits, AllFindings
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_misuse


class TestPotentialHits:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = StubDetector()
        self.misuses = []
        self.uut = PotentialHits(self.detector, self.misuses)

    def test_no_hit(self):
        self.misuses.append(create_misuse("-m1-"))
        finding = Finding({"rank": "no potential hit"})
        finding.is_potential_hit = lambda misuse, y: False

        potential_hits = self.uut.get_potential_hits([finding])

        assert_equals([], potential_hits)

    def test_potential_hit(self):
        self.misuses.append(create_misuse("-m1-"))
        finding = Finding({"rank": ":potential hit for m1:"})
        finding.is_potential_hit = lambda misuse, y: misuse == self.misuses[0]

        potential_hits = self.uut.get_potential_hits([finding])

        assert_equals(self.misuses[0].id, potential_hits[0]["misuse"])

    def test_potential_hit_for_second_misuse(self):
        self.misuses.extend([create_misuse("-1st-"), create_misuse("-2nd-")])
        finding = Finding({"rank": ":some potential hit for second misuse:"})
        finding.is_potential_hit = lambda misuse, y: misuse == self.misuses[1]

        potential_hits = self.uut.get_potential_hits([finding])

        assert_equals(self.misuses[1].id, potential_hits[0]["misuse"])


class TestAllFindings:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = StubDetector()

        self.misuse = create_misuse("-m1-")
        self.misuses = [self.misuse, create_misuse("-m2-")]

        self.uut = AllFindings(self.detector)

    def test_returns_all_findings(self):
        expected = [Finding({"rank": "1", "file": ""}), Finding({"rank": "2", "file": ""})]

        actual = self.uut.get_potential_hits(expected)

        assert_equals(expected, actual)

    def test_limits_number_of_findings(self):
        all = [Finding({"rank": "1"}), Finding({"rank": "2"})]
        self.uut.limit = 1

        actual = self.uut.get_potential_hits(all)

        assert_equals(1, len(actual))
