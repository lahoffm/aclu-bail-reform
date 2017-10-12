# Webscraper for Henry county

* **Currently it is mostly a copy of Athens-Clarke webscraper. Almost all of the code has to be deleted/changed to make it specific for Henry county, feel free to do so.**

* Python 3.6.3
* Retrieves records for [Henry county jail](http://www.henrycountysheriff.net/InmateInformation)
* Uses [```pandas.read_html```](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_html.html)

# Work in progress, copied from Athens-Clarke directory

# How to install and run
* Install [Anaconda](https://www.continuum.io/downloads), open command line
* Create new environment: ```conda create --name python_363 python=3.6.3```
* Activate environment on Windows: ```activate python_363```, Linux/macOS: ```source activate python_363```
* ```cd``` to the Athens-Clarke scraper directory, which contains [```requirements.txt```](requirements.txt)
* ```pip install -r requirements.txt```
* ```python webscraper_main.py``` - writes 2 CSV files into ```../../../data``` as specified in [CONTRIBUTING.md](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md)