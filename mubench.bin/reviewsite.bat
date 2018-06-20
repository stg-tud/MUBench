IF "%~1" == "init" (
  echo "Initializing MUBench review site..."
  docker run --rm -v "%REVIEWSITE_ROOT%":/mubench-reviewsite %REVIEWSITE_DOCKER_IMAGE% /bin/sh -c "composer install --no-interaction --no-dev && mkdir -p upload && mkdir -p logs"
) ELSE IF "%~1" == "start" (
  echo "Starting MUBench review site at http://localhost:%REVIEWSITE_PORT%..."
  docker run --rm -itd -p %REVIEWSITE_PORT%:80 -v "%REVIEWSITE_ROOT%":/mubench-reviewsite --name %REVIEWSITE_DOCKER_CID% %DOCKER_IMAGE%
) ELSE IF "%~1" == "stop" (
  echo "Stopping MUBench review site..."
  docker stop %REVIEWSITE_DOCKER_CID%
) ELSE IF "%~1" == "standalone" (
  IF "%~2" == "start" (
    echo "Starting MUBench review site at http://localhost:%REVIEWSITE_PORT%..."
    docker run --rm -itd -p %REVIEWSITE_PORT%:80 -v %REVIEWSITE_DATA_VOLUME%:/mubench-reviewsite-data --name %REVIEWSITE_DOCKER_CID% %DOCKER_IMAGE%
  ) ELSE IF "%~2" == "stop" (
    echo "Stopping MUBench review site..."
    docker stop %REVIEWSITE_DOCKER_CID%
  ) ELSE IF "%~2" == "reset" (
    echo "Resetting MUBench review site..."
    docker volume rm %REVIEWSITE_DATA_VOLUME%
  ) ELSE (
    echo "Unknown task:" %2
    echo "Chose one of {start,stop,reset}"
  )
) ELSE (
  echo "Unknown task:" %1
  echo "Chose one of {init,start,stop,standalone}"
)
