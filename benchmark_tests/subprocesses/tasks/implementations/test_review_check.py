import yaml
from os import remove
from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals
from nose.tools import assert_in

from benchmark.subprocesses.tasks.implementations.review_check import ReviewCheck
from benchmark.utils.io import remove_tree, write_yaml, create_file, safe_open
from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse


class TestReviewCheck:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = '-detector-'
        self.temp_dir = mkdtemp(prefix='mubench-test-review-check_')
        self.review_dir = join(self.temp_dir, 'reviews')
        self.uut = ReviewCheck("1", self.review_dir, [self.detector])

        self.project = create_project('-project-')
        self.misuse = create_misuse('-misuse-', project=self.project)
        self.version = create_version('-version-', project=self.project, misuses=[self.misuse])
        self.review_folder = join(self.review_dir, self.detector, self.project.id, self.version.version_id,
                                  self.misuse.id)

        with safe_open(join(self.review_folder, 'potentialhits.yml'), "w+") as stream:
            yaml.dump_all([{'id': 0}], stream)

        create_file(join(self.review_folder, 'review.html'))

        self.review_index = 0

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_continues_on_no_review_prepared(self):
        remove(join(self.review_folder, 'review.html'))
        self.run_uut()
        self.assert_problems_equal({})

    def test_warns_for_missing_reviews(self):
        self.run_uut()
        self.assert_problems_equal({0: ['missing 2 review(s) for hit 0']})

    def test_warns_for_missing_reviews_with_existing_review(self):
        self.add_review('-reviewer-', [(0, ['missing null check'])])
        self.run_uut()
        self.assert_problem('missing 1 review(s) for hit 0', 0)

    def test_warns_for_differing_characteristics(self):
        self.add_review('-reviewer1-', [(0, ['-characteristic_a-', '-characteristic_b-'])])
        self.add_review('-reviewer2-', [(0, ['-characteristic_b-', '-characteristic_c-'])])
        self.run_uut()
        self.assert_problems_equal({0: ['differing characteristics: -characteristic_a-, -characteristic_c-']})

    def test_warns_for_missing_reviewer_name(self):
        self.add_review(None, [(0, [])])
        self.run_uut()
        self.assert_problem('review0.yml: unknown reviewer', 0)

    def test_warns_for_unknown_hit_id(self):
        self.add_review('-reviewer-', [(-1, ['-characteristic-'])])
        self.run_uut()
        self.assert_problem('review0.yml: unknown hit id -1', -1)

    def run_uut(self):
        self.uut.start()
        response = self.uut.process_project(self.project)
        self.uut.end()
        return response

    def add_review(self, reviewer, hits):
        review_yml = {'reviewer': reviewer, 'hits': []}
        for hit in hits:
            review_yml['hits'].append({'id': hit[0], 'characteristics': hit[1]})
        write_yaml(review_yml, join(self.review_folder, 'review{}.yml'.format(self.review_index)))
        self.review_index += 1

    def assert_problem(self, expected_problem: str, hit_id: int):
        assert_in(expected_problem,
                  ReviewCheck.problems[self.detector][self.project.id][self.version.version_id][self.misuse.misuse_id][
                      hit_id])

    def assert_problems_equal(self, expected_problems):
        assert_equals(expected_problems, ReviewCheck.problems[self.detector][self.project.id][self.version.version_id][
            self.misuse.misuse_id])
