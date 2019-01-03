docker run --rm -it -v "%MUBENCH_ROOT%":/mubench -v %PIPELINE_CHECKOUTS_VOLUME%:/mubench/checkouts -v %PIPELINE_FINDINGS_VOLUME%:/mubench/findings %PIPELINE_DOCKER_IMAGE% /bin/bash
