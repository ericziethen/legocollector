@echo off

setlocal

set PROJ_MAIN_DIR=%~dp0..
set PACKAGE_ROOT=legocollector

pushd "%PROJ_MAIN_DIR%\%PACKAGE_ROOT%"

set IMPORT_DATE=2019.12.04

set REBRICKABLE_CSV_FILES_DIR=D:\Downloads\Finished\# Lego\rebrickable.com\Downloads\%IMPORT_DATE%
set REBRICKABLE_PART_SCRAPE_FILE_PATH=D:\Downloads\Finished\# Lego\rebrickable.com\Scraped\%IMPORT_DATE%\parts_scraped.json
set BRICKLINK_PART_FILE_PATH=D:\Downloads\Finished\# Lego\bricklink.com\%IMPORT_DATE%\Parts.xml
set LDRAW_PARTS_FILE_PATH=D:\Downloads\Finished\# Lego\ldraw\# Processed Data\%IMPORT_DATE%\ldraw_studcount.json

echo %date% - %time%

rem Check our Files Exists
if not exist "%REBRICKABLE_CSV_FILES_DIR%" echo Cannot find "%REBRICKABLE_CSV_FILES_DIR%" & goto error
if not exist "%REBRICKABLE_PART_SCRAPE_FILE_PATH%" echo Cannot find "%REBRICKABLE_PART_SCRAPE_FILE_PATH%" & goto error
if not exist "%BRICKLINK_PART_FILE_PATH%" echo Cannot find "%BRICKLINK_PART_FILE_PATH%" & goto error
if not exist "%LDRAW_PARTS_FILE_PATH%" echo Cannot find "%LDRAW_PARTS_FILE_PATH%" & goto error

rem Show Initial Counts
python manage.py show_db_details
rem Import the Rebrickable Data
python manage.py import_rebrickable_data "%REBRICKABLE_CSV_FILES_DIR%"
if %errorlevel% gtr 0 goto error
python manage.py show_db_details
if %errorlevel% gtr 0 goto error

rem Import Rebrickable Scraped Parts Details
python manage.py import_rebrickable_scraped_parts "%REBRICKABLE_PART_SCRAPE_FILE_PATH%"
if %errorlevel% gtr 0 goto error
python manage.py show_db_details
if %errorlevel% gtr 0 goto error

rem Import the Bricklink Attributes
python manage.py import_bricklink_attributes "%BRICKLINK_PART_FILE_PATH%"
if %errorlevel% gtr 0 goto error
python manage.py show_db_details
if %errorlevel% gtr 0 goto error

rem Import the Ldraw Attributes
python manage.py import_ldraw_processed_parts "%LDRAW_PARTS_FILE_PATH%"
if %errorlevel% gtr 0 goto error
python manage.py show_db_details
if %errorlevel% gtr 0 goto error

rem Guess the Part Dimensions from Name for non set ones
python manage.py guess_dimensions_from_part_names
if %errorlevel% gtr 0 goto error
python manage.py show_db_details
if %errorlevel% gtr 0 goto error

rem Set the Related Attributes
python manage.py set_related_attributes
if %errorlevel% gtr 0 goto error
python manage.py show_db_details
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
