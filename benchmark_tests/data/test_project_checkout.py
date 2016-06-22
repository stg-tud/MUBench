import os
from tempfile import mkdtemp

from nose.tools import assert_equals
from os.path import join, exists

from shutil import rmtree

from benchmark.data.project_checkout import GitProjectCheckout, LocalProjectCheckout, SVNProjectCheckout
from benchmark.utils.io import remove_tree
from benchmark.utils.shell import Shell


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

        uut.create()

        expected_checkout_path = join(self.checkouts_dir, "-project-", "checkout")
        assert_equals(expected_checkout_path, uut.checkout_dir)
        assert exists(join(expected_checkout_path, "some.file"))

    def test_not_exists(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")
        assert not uut.exists()

    def test_exists_after_create(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")
        uut.create()
        assert uut.exists()

    def test_not_exists_empty(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")
        os.makedirs(uut.checkout_dir)
        assert not uut.exists()

    def test_delete(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")
        uut.create()
        uut.delete()
        assert not exists(uut.checkout_dir)

    def test_to_string(self):
        uut = LocalProjectCheckout(self.local_url, self.checkouts_dir, "-project-")

        assert_equals("synthetic:{}".format(self.local_url), str(uut))


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
        uut = GitProjectCheckout(self.git_url, self.checkouts_dir, "-project-", "-id-", "HEAD")

        uut.create()

        assert exists(join(self.checkouts_dir, "-project-", "checkout", ".git"))

    def test_create_copies_and_checks_out_repo(self):
        uut = GitProjectCheckout(self.git_url, self.checkouts_dir, "-project-", "-id-", "HEAD")

        uut.create()

        expected_checkout_path = join(self.checkouts_dir, "-project-", "-id-", "checkout")
        assert_equals(expected_checkout_path, uut.checkout_dir)
        assert exists(join(expected_checkout_path, ".git"))

    def test_not_exists(self):
        uut = GitProjectCheckout(self.git_url, self.checkouts_dir, "-project-", "-id-", "HEAD")
        assert not uut.exists()

    def test_exists_after_create(self):
        uut = GitProjectCheckout(self.git_url, self.checkouts_dir, "-project-", "-id-", "HEAD")
        uut.create()
        assert uut.exists()

    def test_not_exists_broken(self):
        uut = GitProjectCheckout(self.git_url, self.checkouts_dir, "-project-", "-id-", "HEAD")
        os.makedirs(join(uut.checkout_dir, ".git"))
        assert not uut.exists()

    def test_delete(self):
        uut = GitProjectCheckout(self.git_url, self.checkouts_dir, "-project-", "-id-", "HEAD")
        uut.create()
        uut.delete()
        assert not exists(join(self.checkouts_dir, "-project-", "checkout"))
        assert not exists(uut.checkout_dir)

    def test_to_string(self):
        uut = GitProjectCheckout(self.git_url, self.checkouts_dir, "-project-", "-id-", "-revision-")

        assert_equals("git:{}#-revisio".format(self.git_url), str(uut))


class TestSVNProjectCheckout:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.shell = Shell()

    def test_to_string(self):
        uut = SVNProjectCheckout("-url-", "-path-", "-project-", "-id-", "-revision-")

        assert_equals("svn:-url-@-revision-", str(uut))
