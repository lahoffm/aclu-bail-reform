@echo off

REM Modify next line to activate your Python 3.6.3 environment.
REM You should set up this environment prior to running this batchfile.
REM I used Anaconda but you can run whatever activation command you want.
call activate python_363

REM 2>&1 is to send stderr to logfile, not just stdout

python get_log_file_name.py glynn > tmp
set /p glynn_fname= < tmp
del tmp
cd ../glynn
start "Glynn Webscraper" cmd /c "python webscraper_main.py >> %%glynn_fname%% 2>&1"

cd ../autorun_webscrapers
python get_log_file_name.py ac > tmp
set /p ac_fname= < tmp
del tmp
cd ../athens-clarke
start "AC Webscraper" cmd /c "python webscraper_main.py >> %%ac_fname%% 2>&1"

cd ..\autorun_webscrapers
echo on
