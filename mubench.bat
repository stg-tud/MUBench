@ECHO OFF

SET SCRIPT_DIR=%~dp0
docker run -v "%SCRIPT_DIR%":/mubench.py svamann/mubench ./mubench.py %*
