@ECHO OFF

SET DOCKER_IMAGE_USERNAME=svamann
SET DOCKER_IMAGE_TAG=latest
SET PIPELINE_CHECKOUTS_VOLUME=mubench-checkouts
SET PIPELINE_FINDINGS_VOLUME=mubench-findings
SET REVIEWSITE_DOCKER_CID=mubench-reviewsite-standalone
SET REVIEWSITE_PORT=8080
SET REVIEWSITE_DATA_VOLUME=mubench-reviews

SET SCRIPT_DIR=%~dp0
SET "SCRIPT_DIR=%SCRIPT_DIR:\=/%"
MUBENCH_ROOT=%SCRIPT_DIR%

IF "%~1" == "reviewsite" (
  SET DOCKER_IMAGE=%DOCKER_IMAGE_USERNAME%/mubench-reviewsite:%DOCKER_IMAGE_TAG%
  SET REVIEWSITE_ROOT=%MUBENCH_ROOT%\mubench.reviewsite

  IF "%~2" == "init" (
    echo "Initializing MUBench review site..."
    docker run --rm -v "%REVIEWSITE_ROOT%":/mubench-reviewsite %DOCKER_IMAGE% /bin/bash ./configure.sh
  ) ELSE IF "%~2" == "start" (
    echo "Starting MUBench review site at http://localhost:%REVIEWSITE_PORT%..."
    docker run --rm -itd -p %REVIEWSITE_PORT%:80 -v "%REVIEWSITE_ROOT%":/mubench-reviewsite --name %REVIEWSITE_DOCKER_CID% %DOCKER_IMAGE%
  ) ELSE IF "%~2" == "stop" (
    echo "Stopping MUBench review site..."
    docker stop %REVIEWSITE_DOCKER_CID%
  ) ELSE IF "%~2" == "standalone" (
    IF "%~3" == "start" (
      echo "Starting MUBench review site at http://localhost:%REVIEWSITE_PORT%..."
      docker run --rm -itd -p %REVIEWSITE_PORT%:80 -v %REVIEWSITE_DATA_VOLUME%:/mubench-reviewsite-data --name %REVIEWSITE_DOCKER_CID% %DOCKER_IMAGE%
    ) ELSE IF "%~3" == "stop" (
      echo "Stopping MUBench review site..."
      docker stop %REVIEWSITE_DOCKER_CID%
    ) ELSE IF "%~3" == "reset" (
      echo "Resetting MUBench review site..."
      docker volume rm %REVIEWSITE_DATA_VOLUME%
    ) ELSE (
      echo "Unknown task:" %3
      echo "Chose one of {start,stop,reset}"
    )
  ) ELSE (
    echo "Unknown task:" %2
    echo "Chose one of {init,start,stop,standalone}"
  )
) ELSE (
  SET DOCKER_IMAGE=%DOCKER_IMAGE_USERNAME%/mubench-pipeline:%DOCKER_IMAGE_TAG%
  docker run --rm -v "%MUBENCH_ROOT%":/mubench -v %PIPELINE_CHECKOUTS_VOLUME%:/mubench/checkouts -v %PIPELINE_FINDINGS_VOLUME%:/mubench/findings %DOCKER_IMAGE% python ./mubench.pipeline/benchmark.py %*
)
