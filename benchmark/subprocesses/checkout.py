import logging

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.datareader import DataReaderSubprocess
from benchmark.utils.shell import CommandFailedError


class Checkout(DataReaderSubprocess):
    def __init__(self, checkouts_path: str, force_checkout: bool):
        self.checkouts_path = checkouts_path
        self.force_checkout = force_checkout

    def run(self, misuse: Misuse) -> bool:
        logger = logging.getLogger("checkout")

        try:
            checkout = misuse.get_checkout(self.checkouts_path)
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
