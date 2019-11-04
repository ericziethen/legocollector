@echo off

setlocal

set PROJ_MAIN_DIR=%~dp0..
set PACKAGE_ROOT=legocollector

pushd "%PROJ_MAIN_DIR%\%PACKAGE_ROOT%"

set SCRAPE_DATE=2019.11.04

set REBRICKABLE_CSV_PART_FILE_PATH=D:\Downloads\Finished\# Lego\rebrickable.com\Downloads\%SCRAPE_DATE%\parts.csv
set SCRAPE_JSON_PATH=D:\Downloads\Finished\# Lego\rebrickable.com\Scraped\%SCRAPE_DATE%\parts_scraped.json

set /p REBRICKABLE_TOKEN="Enter Rebrickable.com Token: "

echo %date% - %time%

rem Scrape the Parts
python manage.py scrape_rebrickable_parts "%REBRICKABLE_TOKEN%" "%SCRAPE_JSON_PATH%" --parts_from_csv "%REBRICKABLE_CSV_PART_FILE_PATH%"
if %errorlevel% gtr 0 goto error

goto end

:error
echo ### DATA IMPORT WITH ERRORS ###
echo exit /B 1
exit /B 1

:end
echo %date% - %time%
echo ### DATA IMPORT OK ###
popd
endlocal
echo exit /B 0
exit /B 0
