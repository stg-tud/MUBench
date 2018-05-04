SET SCRIPT_DIR=%~dp0
SET MUBENCH_ROOT=%SCRIPT_DIR%
SET TASKS=%MUBENCH_ROOT%mubench.bin\

CALL %TASKS%environment.bat

IF "%~1" == "-h" (
  docker run --rm -v "%MUBENCH_ROOT%":/mubench %PIPELINE_DOCKER_IMAGE% python3 %MUBENCH_DOCS%/mubench.py %*
  EXIT 0
)

SET TASK=%TASKS%%~1.bat
SET DOC=%MUBENCH_DOCS%%~1.py
IF EXIST %TASK% (
  SHIFT
  IF %~1 == "-h" (
    IF EXIST %DOC% (
      docker run --rm -v "%MUBENCH_ROOT%":/mubench %PIPELINE_DOCKER_IMAGE% python3 %DOC% %*
	  EXIT 0
	)
  )
  CALL %TASK% %*
) ELSE (
  CALL %TASKS%pipeline.bat %*
)