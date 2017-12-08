@echo off
REM Runs multiple webscrapers simultaneously by opening new command windows for each scraper
REM Outputs each scrapers's stdout and stderr into timestamped log file in 'logs' folder
REM This works for Windows 10

setlocal ENABLEDELAYEDEXPANSION
set "start_dir=%cd%"

REM Modify next line to activate your Python 3.6.3 environment.
REM You should set up this environment prior to running this batchfile.
REM I used Anaconda but you can run whatever activation command you want.
call activate python_363

REM Counties cannot have spaces, and must match name of the folder containing
REM the main scrape program for that county.
set counties= athens-clarke bibb\jailCrawler cobb dekalb glynn muscogee

REM we want Cobb to scrape 30 days ago because that gives us the most complete
REM info about a booking, Cobb doesn't allow for more than 30 days in past.
REM if more recent dates are desired you can run python cobb_scraper_30days.py

REM We want Dekalb to scrape yesterday's records because
REM sometimes today's records aren't updated until tomorrow.
python get_yesterday_date.py > tmp
set /p yesterday= < tmp
del tmp

for %%i in (%counties%) do (

    REM make log file name for county
    python get_log_file_name.py %%i > tmp
    set /p log_fname= < tmp
    del tmp
    
    REM go to folder containing main webscraper program
    cd ../%%i
    
    REM "scrape_cmd" is what you would enter on command line if you
    REM wanted to run each scraper individually
    IF "%%i"=="athens-clarke" (
        set scrape_cmd= python webscraper_main.py
    )
    IF "%%i"=="bibb\jailCrawler" (
        set scrape_cmd= scrapy crawl bibb
    )  
    IF "%%i"=="cobb" (
        set scrape_cmd= python cobb_scraper.py 30
    ) 
    IF "%%i"=="dekalb" (
        set scrape_cmd= python webscraper.py custom %yesterday%
    )
    IF "%%i"=="glynn" (
        set scrape_cmd= python webscraper_main.py
    )
    IF "%%i"=="muscogee" (
        set scrape_cmd= python webscraper.py
    )
    
    REM Starts new command window with title %%i running command %%scrape_cmd%%
    REM outputting to logfile %%log_fname%%.
    REM 2>&1 is to send stderr to logfile in addition to stdout
    start "%%i" cmd /c "%%scrape_cmd%% >> %%log_fname%% 2>&1"

    cd %start_dir%
)

echo on
