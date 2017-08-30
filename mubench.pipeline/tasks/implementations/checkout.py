import logging
from typing import List
from tempfile import mkdtemp

from data.project import Project
from data.project_version import ProjectVersion
from tasks.project_version_task import ProjectVersionTask
from utils.shell import CommandFailedError
from utils.io import copy_tree, remove_tree


class Checkout(ProjectVersionTask):
    def __init__(self, checkouts_path: str, force_checkout: bool, use_temp_dir: bool):
        super().__init__()
        self.checkouts_path = checkouts_path
        self.force_checkout = force_checkout
        self.use_temp_dir = use_temp_dir

    def process_project_version(self, project: Project, version: ProjectVersion) -> List[str]:
        logger = logging.getLogger("checkout")

        try:
            checkout = version.get_checkout(self.checkouts_path)
        except ValueError as e:
            logger.error("Checkout data corrupted: %s", e)
            return self.skip(version)

        try:
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
                    temp_checkout.create()
                    logger.debug("Copying checkout to persistent directory...")
                    copy_tree(temp_dir, self.checkouts_path)
                    remove_tree(temp_dir)
                else:
                    checkout.create()

            return self.ok()

        except CommandFailedError as e:
            logger.error("Checkout failed: %s", e)
            return self.skip(version)
        except IOError:
            logger.error("Checkout failed.", exc_info=True)
            return self.skip(version)
