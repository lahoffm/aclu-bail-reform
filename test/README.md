# Testing code folder

* Uses Python 3.6.3

### `csv_format_tester.py` **Under construction**

* Tests that CSV file made by a webscraper is in format described by [CONTRIBUTING.md](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md)
	* Outputs results to a logfile in [`logs`](logs/) folder
	* Even if tests pass, many other things can go wrong, so I recommend eyeball checks of CSV files.
	* `unittest` package [documentation](https://docs.python.org/3/library/unittest.html)
* To run
	* Install [Anaconda](https://www.continuum.io/downloads), open command line
	* Create new environment: ```conda create --name python_363 python=3.6.3```
	* Activate environment on Windows: ```activate python_363```, Linux/macOS: ```source activate python_363```
	* `cd` to this folder
	* `python csv_format_tester.py csv_filename.csv`
	* It automatically looks for the csv file in the local `../data` folder, relative to `csv_format_tester.py` folder.

