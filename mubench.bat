@ECHO OFF

SET SCRIPT_DIR=%~dp0
SET "SCRIPT_DIR=%SCRIPT_DIR:\=/%"
docker run --rm -v "%SCRIPT_DIR%":/mubench svamann/mubench python ./mubench.pipeline/benchmark.py %*
