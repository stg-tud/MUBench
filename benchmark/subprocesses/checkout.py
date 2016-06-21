import logging
from os.path import realpath

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.shell import Shell, CommandFailedError


class Checkout(DataReaderSubprocess):
    def __init__(self, force_checkout: bool, checkout_subdir: str):
        self.data_path = realpath('data')
        self.checkout_base_dir = realpath('checkouts')
        self.checkout_subdir = checkout_subdir
        self.force_checkout = force_checkout

    def run(self, misuse: Misuse) -> bool:
        logger = logging.getLogger("checkout")

        try:
            checkout = misuse.get_checkout(self.checkout_base_dir)
        except ValueError as e:
            logger.error("Checkout data corrupted: %s", e)
            return DataReaderSubprocess.Answer.skip

        try:
            if checkout.exists() and not self.force_checkout:
                logger.info("Already checked out %s.", checkout)
            else:
                logger.info("Fetching %s...", checkout)
                checkout.delete()
                checkout.create()

            return DataReaderSubprocess.Answer.ok

        except CommandFailedError as e:
            logger.error("Checkout failed: %s", e)
            return DataReaderSubprocess.Answer.skip
        except IOError:
            logger.error("Checkout failed.", exc_info=True)
            return DataReaderSubprocess.Answer.skip
