@ECHO OFF

SET SCRIPT_DIR=%~dp0
SET "SCRIPT_DIR=%SCRIPT_DIR:\=/%"

IF "%~1" == "configure" (
  IF "%~2" = "review-site" (
    docker run --rm -v "%SCRIPT_DIR%":/mubench svamann/mubench-ci python /bin/bash ./mubench.reviewsite/configure.sh
  ) ELSE (
    echo "Unknown configuration target:" %2
    echo "Choose one of {review-site}"
  )
) ELSE (
  docker run --rm -v "%SCRIPT_DIR%":/mubench svamann/mubench python ./mubench.pipeline/benchmark.py %*
)
