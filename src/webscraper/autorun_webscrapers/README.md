# Run all webscrapers automatically every day

### Prerequisites
* **Windows 10**: if your system is different, add code & instructions here explaining how to do this on macOS/Linux/etc
* **Python 3.6.3** virtual environment
* Install required packages for each scraper according to their **README.md**
* Test that you can run each scraper individually from command line
* Test that you can run `autorun_webscrapers.py` from command line
* Modify `autorun_webscrapers.bat` so it activates your Python 3.6.3 environment, under the `REM Modify` comment
* Test that you can run `autorun_webscrapers.bat` from command line: `cd` to folder containing batchfile, then `autorun_webscrapers.bat`
* **Don't forget!** Every day, computer must be turned on during the time that you want to run it. Best to be logged in too.

### How to make `autorun_webscrapers.bat` run daily in Windows 10
* **Control Panel** -> **System and Security** -> **Administrative Tools** -> **Task Scheduler**
* **Create Basic Task** -> enter name `autorun_webscrapers` and description
* Hit **Next** a few times, on each screen set what you want.
	* On the **Start a Program** screen by **Program/script** enter path to batchfile like `C:\l\aclu-bail-reform\src\webscraper\autorun_webscrapers\autorun_webscrapers.bat`
	* **Start in (optional)** is NOT optional. It didn't run my task until I entered path to batchfile like `C:\l\aclu-bail-reform\src\webscraper\autorun_webscrapers`
	* On the **Finish** screen check "Open the Properties dialog for this task when I click Finish".
* Set properties
	* **General** tab
		* Select "Run whether user is logged on or not" and "Run with highest privileges"
	* **Conditions** tab
		* UNselect "Start the task only if the computer is idle for", "Stop if the computer switches to battery power", 
		"Start the task only if the computer is on AC power"
		* Select "Wake the computer to run this task"
	* **Settings** tab
		* Select "Run task as soon as possible after a scheduled start is missed"
		* Select "If the task fails, restart every 5 minutes" and "Attempt to restart up to 10 times"
	* When you hit OK, you will be prompted for your login password. It won't accept blanks so if you don't have one, [set one](https://www.google.com/search?&q=change+windows+10+account+password).

### Output
Timestamped logfile in `logs` folder. Logfile contains all stdout and stderr output from whatever code was run.