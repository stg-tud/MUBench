import logging

from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.base.project_version_task import ProjectVersionTask
from benchmark.utils.shell import CommandFailedError


class Checkout(ProjectVersionTask):
    def __init__(self, checkouts_path: str, force_checkout: bool):
        super().__init__()
        self.checkouts_path = checkouts_path
        self.force_checkout = force_checkout

    def process_project_version(self, project: Project, version: ProjectVersion) -> Response:
        logger = logging.getLogger("checkout")

        try:
            checkout = version.get_checkout(self.checkouts_path)
        except ValueError as e:
            logger.error("Checkout data corrupted: %s", e)
            return Response.skip

        try:
            checkout_exists = checkout.exists()
            logger.debug("Checkout exists = %r", checkout_exists)
            if checkout_exists and not self.force_checkout:
                logger.info("Already checked out %s.", version)
            else:
                logger.info("Fetching %s from %s...", version, checkout)
                if self.force_checkout:
                    checkout.delete()
                checkout.create()

            return Response.ok

        except CommandFailedError as e:
            logger.error("Checkout failed: %s", e)
            return Response.skip
        except IOError:
            logger.error("Checkout failed.", exc_info=True)
            return Response.skip
