import logging
from tempfile import mkdtemp
from typing import List

from data.project_checkout import ProjectCheckout
from data.project_version import ProjectVersion
from utils.io import copy_tree, remove_tree


class CheckoutTask:
    def __init__(self, checkouts_path: str, run_timestamp: int, force_checkout: bool, use_temp_dir: bool):
        super().__init__()
        self.checkouts_path = checkouts_path
        self.force_checkout = force_checkout
        self.use_temp_dir = use_temp_dir
        self.run_timestamp = run_timestamp

    def run(self, version: ProjectVersion):
        logger = logging.getLogger("tasks.checkout")

        try:
            checkout = version.get_checkout(self.checkouts_path)
        except ValueError as e:
            raise UserWarning("Checkout data corrupted: %s", e)

        if self.force_checkout:
            checkout.delete()
        checkout_exists = checkout.exists()
        logger.debug("Checkout exists = %r", checkout_exists)
        if checkout_exists:
            logger.debug("Already checked out %s.", version)
        else:
            logger.info("Fetching %s from %s...", version, checkout)
            if self.use_temp_dir:
                temp_dir = mkdtemp(prefix="mubench-checkout_")
                temp_checkout = version.get_checkout(temp_dir)
                temp_checkout.create(self.run_timestamp)
                logger.debug("Copying checkout to persistent directory...")
                copy_tree(temp_dir, self.checkouts_path)
                remove_tree(temp_dir)
            else:
                checkout.create(self.run_timestamp)

        return checkout
