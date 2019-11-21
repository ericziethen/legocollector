@echo off

setlocal

set BATCH_DIR=%~dp0
set PROJ_MAIN_DIR=%BATCH_DIR%..\..
set MODULE_PATH=legocollector

pushd "%PROJ_MAIN_DIR%"

bandit -r "%MODULE_PATH%" --exclude "legocollector/tests/"
set return_code=%errorlevel%
if %return_code% equ 0 (
    echo *** No Issues Found
    goto exit_ok
) else (
    echo *** Some Issues Found
    goto exit_error
)

:exit_error
popd
endlocal
exit /B 1

:exit_ok
popd
endlocal
exit /B 0
