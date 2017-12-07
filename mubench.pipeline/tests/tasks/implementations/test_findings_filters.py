from unittest.mock import MagicMock

from nose.tools import assert_equals

from data.finding import Finding
from tasks.implementations.findings_filters import PotentialHitsFilterTask, AllFindingsFilterTask
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_misuse


class TestPotentialHits:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = StubDetector()
        self.uut = PotentialHitsFilterTask()
        self.detector_run = MagicMock()

    def test_no_hit(self):
        finding = Finding({"rank": "no potential hit"})
        finding.is_potential_hit = lambda misuse, y: False
        self.detector_run.findings = [finding]

        potential_hits = self.uut.run(create_misuse("-m1-"), self.detector_run)

        assert_equals([], potential_hits)

    def test_potential_hit(self):
        finding = Finding({"rank": ":potential hit for m1:"})
        misuse = create_misuse("-m1-")
        finding.is_potential_hit = lambda m, y: m == misuse
        self.detector_run.findings = [finding]

        potential_hits = self.uut.run(misuse, self.detector_run)

        assert_equals(misuse.misuse_id, potential_hits[0]["misuse"])


class TestAllFindings:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = StubDetector()

        self.misuse = create_misuse("-m1-")
        self.misuses = [self.misuse, create_misuse("-m2-")]

        self.detector_run = MagicMock()

        self.uut = AllFindingsFilterTask()

    def test_returns_all_findings(self):
        expected = [
            Finding({"rank": "1", "misuse": "finding-0", "file": ""}),
            Finding({"rank": "2", "misuse": "finding-1", "file": ""})
        ]
        self.detector_run.findings = expected

        actual = self.uut.run(self.detector_run)

        assert_equals(expected, actual)

    def test_limits_number_of_findings(self):
        detector_execution = MagicMock()
        all = [Finding({"rank": "1"}), Finding({"rank": "2"})]
        detector_execution.findings = all
        self.uut.limit = 1

        actual = self.uut.run(detector_execution)

        assert_equals(1, len(actual))
