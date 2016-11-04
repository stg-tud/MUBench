import logging
from typing import List

from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.requirements import GitRequirement, SVNRequirement
from benchmark.tasks.project_version_task import ProjectVersionTask
from benchmark.utils.shell import CommandFailedError


class Checkout(ProjectVersionTask):
    def __init__(self, checkouts_path: str, force_checkout: bool):
        super().__init__()
        self.checkouts_path = checkouts_path
        self.force_checkout = force_checkout

    def get_requirements(self):
        return [GitRequirement(), SVNRequirement()]

    def process_project_version(self, project: Project, version: ProjectVersion) -> List[str]:
        logger = logging.getLogger("checkout")

        try:
            checkout = version.get_checkout(self.checkouts_path)
        except ValueError as e:
            logger.error("Checkout data corrupted: %s", e)
            return self.skip(version)

        try:
            checkout_exists = checkout.exists()
            logger.debug("Checkout exists = %r", checkout_exists)
            if checkout_exists and not self.force_checkout:
                logger.debug("Already checked out %s.", version)
            else:
                logger.info("Fetching %s from %s...", version, checkout)
                if self.force_checkout:
                    checkout.delete()
                checkout.create()

            return self.ok()

        except CommandFailedError as e:
            logger.error("Checkout failed: %s", e)
            return self.skip(version)
        except IOError:
            logger.error("Checkout failed.", exc_info=True)
            return self.skip(version)
