SET PIPELINE_DOCKER_IMAGE=svamann/mubench-pipeline:latest
SET PIPELINE_CHECKOUTS_VOLUME=mubench-checkouts
SET PIPELINE_FINDINGS_VOLUME=mubench-findings
SET REVIEWSITE_DOCKER_IMAGE=svamann/mubench-reviewsite:latest
SET REVIEWSITE_DOCKER_CID=mubench-reviewsite-standalone
SET REVIEWSITE_PORT=8080
SET REVIEWSITE_DATA_VOLUME=mubench-reviews
SET REVIEWSITE_ROOT=%MUBENCH_ROOT%mubench.reviewsite

SET MUBENCH_DOCS=%MUBENCH_ROOT%mubench.docs\