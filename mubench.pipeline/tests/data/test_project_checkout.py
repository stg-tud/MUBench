import os
from os.path import join, exists, realpath, dirname
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from unittest.mock import MagicMock

from nose.tools import assert_equals

from data.project_checkout import GitProjectCheckout, LocalProjectCheckout, SVNProjectCheckout, \
    SyntheticProjectCheckout, ZipProjectCheckout, ProjectCheckout
from utils.io import remove_tree, copy_tree, create_file
from utils.shell import Shell


class ProjectCheckoutTestImpl(ProjectCheckout):
    def __init__(self, base_path: str, url: str = "-url-", name: str = "-test-checkout-"):
        super().__init__(url, base_path, name)

        self.exists = MagicMock()
        self._create = MagicMock()
        self.delete = MagicMock()

    def exists(self) -> bool:
        pass

    def _create(self):
        pass

    def delete(self) -> None:
        pass


class TestProjectCheckout:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-checkout-base_")

    def teardown(self):
        rmtree(self.temp_dir)

    def test_uses_zero_time_if_never_created(self):
        uut = ProjectCheckoutTestImpl(self.temp_dir)
        assert_equals(0, uut.timestamp)

    def test_saves_checkout_time(self):
        test_timestamp = 1516183458
        uut = ProjectCheckoutTestImpl(self.temp_dir)
        uut.create(test_timestamp)
        assert_equals(test_timestamp, uut.timestamp)

    def create_calls_subclass(self):
        uut = ProjectCheckoutTestImpl(self.temp_dir)
        uut.create(0)
        uut._create().assert_called_once()


class TestLocalProjectCheckout:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.shell = Shell()
        self.temp_dir = mkdtemp(prefix="mubench-checkout-local_")
        self.local_url = join(self.temp_dir, "origin")

        os.makedirs(self.local_url)
        open(join(self.local_url, "some.file"), "w").close()

        self.checkouts_dir = join(self.temp_dir, "checkouts")

    def teardown(self):
        rmtree(self.temp_dir)

    def test_create(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")

        uut.create(0)

        expected_checkout_path = join(self.checkouts_dir, "-project-", "checkout")
        assert_equals(expected_checkout_path, uut.checkout_dir)
        assert exists(join(expected_checkout_path, "some.file"))

    def test_not_exists(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")
        assert not uut.exists()

    def test_exists_after_create(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")
        uut.create(0)
        assert uut.exists()

    def test_not_exists_empty(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")
        os.makedirs(uut.checkout_dir)
        assert not uut.exists()

    def test_delete(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")
        uut.create(0)
        uut.delete()
        assert not exists(uut.checkout_dir)

    def test_to_string(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")

        assert_equals("local:{}".format(self.local_url), str(uut))


class TestSyntheticCheckout:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.checkouts_path = mkdtemp(prefix="mubench-checkout-local_")

        self.uut = SyntheticProjectCheckout("-project-", "-id-", self.checkouts_path)

    def test_exists_always(self):
        assert not self.uut.exists()

    def test_create_passes(self):
        self.uut.create(0)

        assert exists(self.uut.checkout_dir)

    def test_delete_passes(self):
        os.makedirs(self.uut.checkout_dir)

        self.uut.delete()

        assert not exists(self.uut.checkout_dir)

    def test_to_string(self):
        assert_equals("synthetic:-project-.-id-", str(self.uut))


class TestZipProjectCheckout:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-checkout-zip_')
        self.checkouts_dir = join(self.temp_dir, "checkouts")
        self.url = "file://" + join(dirname(__file__), "test_project_checkout_bundle.zip")

        revision_md5 = "d2046c17a1ea90a45eb4d20429cd46c8"

        self.uut = ZipProjectCheckout("-project-", "-version-", self.url, revision_md5, self.checkouts_dir)

    def test_create_download_and_unzips(self):
        self.uut.create(0)

        assert exists(join(self.checkouts_dir, "-project-", "-version-", "checkout", "foo"))

    def test_not_exists(self):
        assert not self.uut.exists()

    def test_exists(self):
        checkout_path = join(self.checkouts_dir, "-project-", "-version-", "checkout")
        create_file(join(checkout_path, "bundle.zip"))
        create_file(join(checkout_path, "foo"))

        assert self.uut.exists()

    def test_delete(self):
        checkout_path = join(self.checkouts_dir, "-project-", "-version-", "checkout")
        create_file(join(checkout_path, "bundle.zip"))
        create_file(join(checkout_path, "foo"))

        self.uut.delete()

        assert not exists(checkout_path)

    def test_to_string(self):
        assert_equals("zip:-project-:{}".format(self.url), str(self.uut))


class TestGitProjectCheckout:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-checkout-git_')
        self.git_url = join(self.temp_dir, "remote")

        os.makedirs(self.git_url)
        Shell.exec("git init .", cwd=self.git_url)
        Shell.exec("touch foo", cwd=self.git_url)
        Shell.exec("git add -A", cwd=self.git_url)
        Shell.exec("git commit -a -m \"Initial commit.\"", cwd=self.git_url)

        self.checkouts_dir = join(self.temp_dir, "checkouts")

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_create_clones_repo(self):
        uut = GitProjectCheckout("-project-", "-id-", self.git_url, "HEAD", self.checkouts_dir)

        uut.create(0)

        assert exists(join(self.checkouts_dir, "-project-", "checkout", ".git"))

    def test_create_copies_and_checks_out_repo(self):
        uut = GitProjectCheckout("-project-", "-id-", self.git_url, "HEAD", self.checkouts_dir)

        uut.create(0)

        expected_checkout_path = join(self.checkouts_dir, "-project-", "-id-", "checkout")
        assert_equals(expected_checkout_path, uut.checkout_dir)
        assert exists(join(expected_checkout_path, ".git"))

    def test_not_exists(self):
        uut = GitProjectCheckout("-project-", "-id-", self.git_url, "HEAD", self.checkouts_dir)
        assert not uut.exists()

    def test_exists(self):
        uut = GitProjectCheckout("-project-", "-id-", self.git_url, "HEAD", self.checkouts_dir)
        copy_tree(self.git_url, uut.checkout_dir)

        assert uut.exists()

    def test_not_exists_broken(self):
        uut = GitProjectCheckout("-project-", "-id-", self.git_url, "HEAD", self.checkouts_dir)
        os.makedirs(join(uut.checkout_dir, ".git"))
        assert not uut.exists()

    def test_delete(self):
        uut = GitProjectCheckout("-project-", "-id-", self.git_url, "HEAD", self.checkouts_dir)
        uut.create(0)
        uut.delete()
        assert not exists(join(self.checkouts_dir, "-project-", "checkout"))
        assert not exists(uut.checkout_dir)

    def test_to_string(self):
        uut = GitProjectCheckout("-project-", "-id-", self.git_url, "-revision-", self.checkouts_dir)

        assert_equals("git:{}#-revisio".format(self.git_url), str(uut))


class TestSVNProjectCheckout:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-checkout-svn_')
        self.svn_url = Path(join(dirname(realpath(__file__)), "test_svn")).as_uri()
        self.checkouts_dir = join(self.temp_dir, "checkouts")

        self.uut = SVNProjectCheckout("-project-", "-version-", self.svn_url, "1", self.checkouts_dir)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_not_exists(self):
        assert not self.uut.exists()

    def test_create_checks_repo_out(self):
        self.uut.create(0)

        assert exists(join(self.checkouts_dir, "-project-", "-version-", "checkout"))

    def test_exists(self):
        self.uut.create(0)

        assert self.uut.exists()

    def test_not_exists_no_svn_checkout(self):
        os.makedirs(self.uut.checkout_dir)

        assert not self.uut.exists()

    def test_delete(self):
        self.uut.create(0)
        self.uut.delete()

        assert not exists(self.uut.checkout_dir)

    def test_multiple_versions(self):
        checkout_version2 = SVNProjectCheckout(self.uut.name, "other-version", self.svn_url, "1", self.checkouts_dir)

        self.uut.create(0)
        checkout_version2.create(0)

        assert checkout_version2.exists()

    def test_to_string(self):
        assert_equals("svn:{}@1".format(self.svn_url), str(self.uut))
