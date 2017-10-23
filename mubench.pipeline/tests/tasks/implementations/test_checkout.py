import unittest
from unittest.mock import MagicMock

from nose.tools import assert_equals, assert_raises

from data.project_checkout import ProjectCheckout
from tasks.implementations.checkout import CheckoutTask
from tests.test_utils.data_util import create_project, create_version
from utils.shell import CommandFailedError


class TestCheckout(unittest.TestCase):
    # noinspection PyAttributeOutsideInit
    def setUp(self):
        self.checkout = ProjectCheckout("-url-", "-base_path-", "-name-")
        self.checkout.create = MagicMock()
        self.checkout.delete = MagicMock()

        self.project = create_project("-project-")
        self.version = create_version("-version-", project=self.project)
        self.version.get_checkout = MagicMock(return_value=self.checkout)

        self.uut = CheckoutTask("-checkouts-", force_checkout=False, use_temp_dir=False)

    def test_initial_checkout(self):
        self.checkout.exists = MagicMock(return_value=False)

        response = self.uut.run(self.version)

        self.checkout.delete.assert_not_called()
        self.checkout.create.assert_called_with()
        assert_equals([self.checkout], response)

    def test_exists(self):
        self.checkout.exists = MagicMock(return_value=True)

        response = self.uut.run(self.version)

        self.checkout.delete.assert_not_called()
        self.checkout.create.assert_not_called()
        assert_equals([self.checkout], response)

    def test_error_get_checkout(self):
        self.version.get_checkout = MagicMock(side_effect=ValueError)

        assert_raises(UserWarning, self.uut.run, self.version)

    def test_error_checkout(self):
        self.checkout.exists = MagicMock(return_value=False)
        self.checkout.create = MagicMock(side_effect=CommandFailedError("-cmd-", "-out-"))

        assert_raises(CommandFailedError, self.uut.run, self.version)

    def test_force_checkout(self):
        self.checkout.exists = MagicMock(return_value=False)  # should delete before check
        self.uut.force_checkout = True

        self.uut.run(self.version)

        self.checkout.delete.assert_called_with()
        self.checkout.create.assert_called_with()
