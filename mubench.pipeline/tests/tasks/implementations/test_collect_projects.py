from tempfile import mkdtemp
from unittest.mock import MagicMock

from nose.tools import assert_equals

from tasks.implementations.collect_projects import CollectProjectsTask
from tests.test_utils.data_util import create_project
from utils.data_filter import DataFilter
from utils.io import remove_tree, create_file

NO_FILTER = MagicMock()  # type: DataFilter
NO_FILTER.is_filtered = lambda id_: False


class TestCollectProject:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-datareader-test_')

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_finds_all_projects(self):
        p1 = create_project("p1", base_path=self.temp_dir)
        create_file(p1._project_file)
        p2 = create_project("p2", base_path=self.temp_dir)
        create_file(p2._project_file)
        uut = CollectProjectsTask(self.temp_dir, NO_FILTER)

        actual = uut.run()

        assert_equals([p1, p2], actual)

    def test_uses_filter(self):
        project = create_project("-id-", base_path=self.temp_dir)
        create_file(project._project_file)
        filter_ = MagicMock()  # type: DataFilter
        filter_.is_filtered = lambda id_: id_ == "-id-"
        uut = CollectProjectsTask(self.temp_dir, filter_)

        actual = uut.run()

        assert_equals([], actual)
