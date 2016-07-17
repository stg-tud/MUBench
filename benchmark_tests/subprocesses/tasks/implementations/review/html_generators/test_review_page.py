from os.path import join, exists
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.subprocesses.tasks.implementations.review.html_generators import review_page
from benchmark.utils.io import remove_tree
from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse


class TestReviewPageGenerator:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-review-page-generator_')

        self.test_project = create_project('project')
        self.test_misuse = create_misuse('misuse', project=self.test_project)
        self.test_version = create_version('version', project=self.test_project, misuses=[self.test_misuse])

        self.findings_folder = join(self.temp_dir, 'findings', 'detector', 'project', 'version')
        self.review_folder = join(self.temp_dir, 'reviews', 'detector', 'project', 'version')

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_creates_reviewing_line(self):
        review_page.generate(self.review_folder, self.findings_folder, 'detector', self.test_project, self.test_version,
                             self.test_misuse, [])

        review_file = join(self.review_folder, 'review.html')
        assert exists(review_file)

        with open(review_file) as file:
            actual_lines = file.readlines()

        expected_line = "<p>Reviewing: detector/project/version/project.misuse<hr></p>\n"

        assert_equals(expected_line, actual_lines[0])

    def test_adds_misuse_description(self):
        self.test_misuse._DESCRIPTION = "SubLine.intersection() may return null."

        review_page.generate(self.review_folder, self.findings_folder, 'detector', self.test_project, self.test_version,
                             self.test_misuse, [])

        review_file = join(self.review_folder, 'review.html')
        assert exists(review_file)

        with open(review_file) as file:
            actual_lines = file.readlines()

        expected_line = "<p>SubLine.intersection() may return null.</p>\n"

        assert_equals(expected_line, actual_lines[1])

    def test_adds_fix_description(self):
        self.test_misuse.fix.description = "Check result before using."

        review_page.generate(self.review_folder, self.findings_folder, 'detector', self.test_project, self.test_version,
                             self.test_misuse, [])

        review_file = join(self.review_folder, 'review.html')
        assert exists(review_file)

        with open(review_file) as file:
            actual_lines = file.readlines()

        expected_line = "<p>Check result before using.</p>\n"

        assert_equals(expected_line, actual_lines[2])

    def test_adds_misuse_characteristics(self):
        self.test_misuse._characteristics = ["missing/condition/null_check"]

        review_page.generate(self.review_folder, self.findings_folder, 'detector', self.test_project, self.test_version,
                             self.test_misuse, [])

        review_file = join(self.review_folder, 'review.html')
        assert exists(review_file)

        with open(review_file) as file:
            actual_lines = file.readlines()

        expected_lines = ["<p>Characteristics:<br/>\n", " - missing/condition/null_check<br/>\n", "</p>\n"]

        assert_equals(expected_lines, actual_lines[3:6])

    def test_adds_location(self):
        self.test_misuse.location.file = "org.apache...SubLine"
        self.test_misuse.location.method = "intersection(SubLine subLine, bool include...)"

        review_page.generate(self.review_folder, self.findings_folder, 'detector', self.test_project, self.test_version,
                             self.test_misuse, [])

        review_file = join(self.review_folder, 'review.html')
        assert exists(review_file)

        with open(review_file) as file:
            actual_lines = file.readlines()

        expected_line = "<p>In org.apache...SubLine.intersection(SubLine subLine, bool include...)</p>\n"

        assert_equals(expected_line, actual_lines[5])

    def test_adds_hr_line_after_misuse_information(self):
        review_page.generate(self.review_folder, self.findings_folder, 'detector', self.test_project, self.test_version,
                             self.test_misuse, [])

        review_file = join(self.review_folder, 'review.html')
        assert exists(review_file)

        with open(review_file) as file:
            actual_lines = file.readlines()

        expected_line = "<hr>\n"

        assert_equals(expected_line, actual_lines[6])

    def test_adds_potential_hit_information(self):
        potential_hits = [{"missingcalls": ["getAngle()"]}, {"additionalkey": "additional information"}]

        review_page.generate(self.review_folder, self.findings_folder, 'detector', self.test_project, self.test_version,
                             self.test_misuse, potential_hits)

        review_file = join(self.review_folder, 'review.html')
        assert exists(review_file)

        with open(review_file) as file:
            actual_lines = file.readlines()

        expected_lines = ["Potential Hits<br/>\n",
                          "<table border=\"1\" cellpadding=\"5\">\n",
                          "<tr>\n",
                          "<th>additionalkey</th>\n",
                          "<th>missingcalls</th>\n",
                          "</tr>\n",
                          "<tr>\n",
                          "<td></td>\n",
                          "<td>['getAngle()']</td>\n",
                          "</tr>\n",
                          "<tr>\n",
                          "<td>additional information</td>\n",
                          "<td></td>\n",
                          "</tr>\n",
                          "</table>\n"]

        actual_table_lines = actual_lines[7:]
        assert_equals(expected_lines, actual_table_lines)
