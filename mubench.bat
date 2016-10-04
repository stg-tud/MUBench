@ECHO OFF

SET SCRIPT_DIR=%~dp0
SET "SCRIPT_DIR=%SCRIPT_DIR:\=/%"
docker run -v "%SCRIPT_DIR%":/mubench svamann/mubench ./mubench.py %*
