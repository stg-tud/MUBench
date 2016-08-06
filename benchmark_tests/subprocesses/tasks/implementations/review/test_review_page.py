import os
from os.path import join, exists
from tempfile import mkdtemp

from nose.tools import assert_in

from benchmark.subprocesses.tasks.implementations.review import review_page
from benchmark.utils.io import remove_tree, create_file
from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse


class TestReviewPageGenerator:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-review-page-generator_')
        os.chdir(self.temp_dir)

        self.test_project = create_project('project')
        self.test_misuse = create_misuse('misuse', project=self.test_project)
        self.test_version = create_version('version', project=self.test_project, misuses=[self.test_misuse])
        self.compiles_path = join(self.temp_dir, 'checkouts')

        original_src_file = 'foo.java'
        original_src_folder = self.test_version.get_compile(self.compiles_path).original_sources_path
        self.original_src_file_path = join(original_src_folder, original_src_file)
        create_file(self.original_src_file_path)

        self.test_misuse.location.file = original_src_file
        self.test_misuse.location.method = 'bar()'

        self.findings_folder = join(self.temp_dir, 'findings', 'detector', 'project', 'version')
        self.review_file = join(self.temp_dir, 'reviews', 'detector', 'project', 'version', 'review.html')

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_creates_reviewing_line(self):
        self.generate_review_page([])

        content = self.read_review_file()
        assert_in("<h1>Review</h1>", content)

    def test_adds_misuse_description(self):
        self.test_misuse._DESCRIPTION = "SubLine.intersection() may return null."

        self.generate_review_page([])

        content = self.read_review_file()
        assert_in("<tr><td class=\"vtop\"><b>Description:</b></td><td>SubLine.intersection() may return null.</td></tr>", content)

    def test_adds_fix_description(self):
        self.test_misuse.fix.description = "Check result before using."
        self.test_misuse.fix.commit = "http://diff.webview"

        self.generate_review_page([])

        content = self.read_review_file()
        assert_in("<tr><td class=\"vtop\"><b>Fix Description:</b></td><td>Check result before using. "
                  "(<a href=\"http://diff.webview\">see diff</a>)</td></tr>", content)

    def test_adds_misuse_characteristics(self):
        self.test_misuse._characteristics = ["missing/condition/null_check"]

        self.generate_review_page([])

        content = self.read_review_file()
        assert_in("""<tr><td class="vtop"><b>Violation Types:</b></td><td><ul>
                <li>missing/condition/null_check</li>
            </ul></td></tr>""", content)

    def test_adds_location(self):
        self.test_misuse.location.file = "foo.java"
        self.test_misuse.location.method = "bar()"

        self.generate_review_page([])

        content = self.read_review_file()
        assert_in("<tr><td><b>In File:</b></td><td>foo.java</td></tr>", content)
        assert_in("<tr><td><b>In Method:</b></td><td>bar()</td></tr>", content)

    def test_adds_potential_hit_information(self):
        potential_hits = [{"id": 42, "info1": "x"}]

        self.generate_review_page(potential_hits)

        content = self.read_review_file()
        assert_in("<th>id</th><th>info1</th>", content)
        assert_in("<td>42</td><td>x</td>", content)

    def test_orders_potential_hit_information(self):
        potential_hits = [{"id": 666, "info_z": "x", "info_a": "y"}]

        self.generate_review_page(potential_hits)

        content = self.read_review_file()
        assert_in("<th>id</th><th>info_a</th><th>info_z</th>", content)
        assert_in("<td>666</td><td>y</td><td>x</td>", content)

    def test_formats_potential_hit_list_information(self):
        potential_hits = [{"id": 1, "missingcalls": ["a", "b"]}]

        # noinspection PyTypeChecker
        self.generate_review_page(potential_hits)

        content = self.read_review_file()
        assert_in("""<td><ul>
                <li>a</li>
                <li>b</li>
            </ul></td>""", content)

    def test_adds_potential_hit_information_of_all_hits(self):
        potential_hits = [{"id": 1, "a": "x"}, {"id": 2, "b": "y"}]

        self.generate_review_page(potential_hits)

        content = self.read_review_file()
        assert_in("<th>id</th><th>a</th><th>b</th>", content)
        assert_in("<td>1</td><td>x</td><td></td>", content)
        assert_in("<td>2</td><td></td><td>y</td>", content)

    def generate_review_page(self, potential_hits):
        review_page.generate("test-ex", self.review_file, 'detector', self.compiles_path, self.test_version,
                             self.test_misuse, potential_hits)

    def test_adds_target_code_method_only(self):
        with open(self.original_src_file_path, 'w+') as target:
            target.write("class C {\n  void bar() {}\n}")
        self.generate_review_page([])
        content = self.read_review_file()
        assert_in("<code class=\"language-java\">class C {\n  void bar() {}\n}</code>", content)

    def read_review_file(self):
        assert exists(self.review_file)
        with open(self.review_file) as file:
            actual_lines = file.readlines()
        return "".join(actual_lines)
