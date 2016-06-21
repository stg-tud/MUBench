import unittest
from unittest.mock import MagicMock

from nose.tools import assert_equals

from benchmark.data.project_checkout import ProjectCheckout
from benchmark.subprocesses.checkout import Checkout
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.shell import Shell, CommandFailedError
from benchmark_tests.data.test_misuse import create_misuse


class TestCheckout(unittest.TestCase):
    # noinspection PyAttributeOutsideInit
    def setUp(self):
        self.checkout = ProjectCheckout(":url:", ":base_path:", ":name:")
        self.checkout.create = MagicMock()
        self.checkout.delete = MagicMock()

        self.misuse = create_misuse()
        self.misuse.get_checkout = MagicMock(return_value=self.checkout)

        self.uut = Checkout(checkout_parent=False, setup_revisions=False, checkout_subdir="")

    def test_initial_checkout(self):
        self.checkout.exists = MagicMock(return_value=False)

        answer = self.uut.run(self.misuse)

        self.checkout.delete.assert_called_with()
        self.checkout.create.assert_called_with()
        assert_equals(DataReaderSubprocess.Answer.ok, answer)

    def test_exists(self):
        self.checkout.exists = MagicMock(return_value=True)

        answer = self.uut.run(self.misuse)

        self.checkout.delete.assert_not_called()
        self.checkout.create.assert_not_called()
        assert_equals(DataReaderSubprocess.Answer.ok, answer)

    def test_error_get_checkout(self):
        self.misuse.get_checkout = MagicMock(side_effect=ValueError)

        answer = self.uut.run(self.misuse)

        assert_equals(DataReaderSubprocess.Answer.skip, answer)

    def test_error_checkout(self):
        self.checkout.exists = MagicMock(return_value=False)
        self.checkout.create = MagicMock(side_effect=CommandFailedError(":cmd:", ":out:"))

        answer = self.uut.run(self.misuse)

        assert_equals(DataReaderSubprocess.Answer.skip, answer)

