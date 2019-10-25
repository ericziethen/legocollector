@echo off

setlocal

set PROJ_MAIN_DIR=%~dp0..
set PACKAGE_ROOT=legocollector

pushd "%PROJ_MAIN_DIR%\%PACKAGE_ROOT%"

set REBRICKABLE_CSV_FILES_DIR=D:\Downloads\Finished\# Lego\rebrickable.com\Downloads\2019.10.22
set REBRICKABLE_PART_SCRAPE_FILE_PATH=D:\Downloads\Finished\# Lego\rebrickable.com\Scraped\2019.10.22\parts_scraped.json
set BRICKLINK_PART_FILE_PATH=D:\Downloads\Finished\# Lego\bricklink.com\2019.10.22\Parts.xml

echo %date% - %time%

rem Import the Rebrickable Data
python manage.py import_rebrickable_data "%REBRICKABLE_CSV_FILES_DIR%"
if %errorlevel% gtr 0 goto error

rem Guess the Part Dimensions from Name
python manage.py guess_dimensions_from_part_names
if %errorlevel% gtr 0 goto error

rem Import Rebrickable Scraped Parts Details
python manage.py import_rebrickable_scraped_parts "%REBRICKABLE_PART_SCRAPE_FILE_PATH%"
if %errorlevel% gtr 0 goto error

rem Import the Bricklink Attributes
python manage.py import_bricklink_attributes "%BRICKLINK_PART_FILE_PATH%"
if %errorlevel% gtr 0 goto error

rem Set the Related Attributes
python manage.py set_related_attributes
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
