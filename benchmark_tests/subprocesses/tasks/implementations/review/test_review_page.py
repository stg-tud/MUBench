import os
from os.path import join, exists
from tempfile import mkdtemp

from nose.tools import assert_in

from benchmark.subprocesses.tasks.implementations.review import potential_hits_section
from benchmark.subprocesses.tasks.implementations.review import review_page
from benchmark.utils.io import remove_tree, safe_open, create_file
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
        self.review_folder = join(self.temp_dir, 'reviews', 'detector', 'project', 'version')

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_creates_reviewing_line(self):
        review_page.generate(self.review_folder, 'detector', self.compiles_path, self.test_project, self.test_version,
                             self.test_misuse, [])

        content = self.read_review_file()
        assert_in("<h1>Review: detector/project/version/project.misuse</h1>", content)

    def test_adds_misuse_description(self):
        self.test_misuse._DESCRIPTION = "SubLine.intersection() may return null."

        review_page.generate(self.review_folder, 'detector', self.compiles_path, self.test_project, self.test_version,
                             self.test_misuse, [])

        content = self.read_review_file()
        assert_in("<b>Description:</b> SubLine.intersection() may return null.", content)

    def test_adds_fix_description(self):
        self.test_misuse.fix.description = "Check result before using."

        review_page.generate(self.review_folder, 'detector', self.compiles_path, self.test_project, self.test_version,
                             self.test_misuse, [])

        content = self.read_review_file()
        assert_in("<b>Fix Description:</b> Check result before using.", content)

    def test_adds_misuse_characteristics(self):
        self.test_misuse._characteristics = ["missing/condition/null_check"]

        review_page.generate(self.review_folder, 'detector', self.compiles_path, self.test_project, self.test_version,
                             self.test_misuse, [])

        content = self.read_review_file()
        assert_in("<b>Misuse Elements:</b><ul>\n<li>missing/condition/null_check</li>\n</ul>", content)

    def test_adds_location(self):
        self.test_misuse.location.file = "foo.java"
        self.test_misuse.location.method = "bar()"
        self.test_misuse.fix.commit = "http://commit.url"

        review_page.generate(self.review_folder, 'detector', self.compiles_path, self.test_project, self.test_version,
                             self.test_misuse, [])

        content = self.read_review_file()
        assert_in("<b>In File:</b> <a href=\"http://commit.url\">foo.java</a>,"
                  " <b>Method:</b> bar()", content)

    def test_adds_potential_hit_information(self):
        potential_hits = [{"missingcalls": ["getAngle()"]}, {"additionalkey": "additional information"}]

        review_page.generate(self.review_folder, 'detector', self.compiles_path, self.test_project, self.test_version,
                             self.test_misuse, potential_hits)

        content = self.read_review_file()
        assert_in("<h2>Potential Hits</h2>\n<table border=\"1\" cellpadding=\"5\">\n"
                  "<tr>\n<th>additionalkey</th>\n<th>missingcalls</th>\n</tr>\n"
                  "<tr>\n<td></td>\n<td><ul>\n<li>getAngle()</li>\n</ul></td>\n</tr>\n"
                  "<tr>\n<td>additional information</td>\n<td></td>\n</tr>\n"
                  "</table>\n", content)

    def test_uses_detector_specific_potential_hits_generator(self):
        potential_hits = [{"missingcalls": ["getAngle()"]}, {"additionalkey": "additional information"}]

        def detector(potential_hits):
            return ['-whatever-']

        setattr(potential_hits_section, 'detector', detector)

        review_page.generate(self.review_folder, 'detector', self.compiles_path, self.test_project, self.test_version,
                             self.test_misuse, potential_hits)

        content = self.read_review_file()
        assert_in('-whatever-', content)

    def test_adds_target_code_method_only(self):
        with open(self.original_src_file_path, 'w+') as target:
            target.write("class C { void bar() {} }")
        review_page.generate(self.review_folder, 'detector', self.compiles_path, self.test_project, self.test_version,
                             self.test_misuse, [])
        content = self.read_review_file()
        assert_in("<code class=\"language-java\">void bar() {\n}\n</code>", content)

    def read_review_file(self):
        review_file = join(self.review_folder, 'review.html')
        assert exists(review_file)
        with open(review_file) as file:
            actual_lines = file.readlines()
        return "".join(actual_lines)
