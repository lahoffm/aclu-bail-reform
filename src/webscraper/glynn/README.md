# Webscraper for Glynn county
* Python 3.6.3
* Retrieves daily jail population PDF from [Glynn county jail](http://www.glynncountysheriff.org/)

## How to install and run
* Install [Anaconda](https://www.continuum.io/downloads), open command line
* Create new environment: ```conda create --name python_363 python=3.6.3```
* Activate environment on Windows: ```activate python_363```, Linux/macOS: ```source activate python_363```
* ```cd``` to the Glynn scraper directory, which contains [```requirements.txt```](requirements.txt)
* ```pip install -r requirements.txt```
* ```python webscraper_main.py``` - writes CSV file into ```../../../data``` as specified in [CONTRIBUTING.md](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md)
	* You may get an error when calling a `tabula-py` library function. See below.

## Get tabula-py working (Windows 10)
* From [PyPi](https://pypi.python.org/pypi/tabula-py/1.0.0) and [Github](https://github.com/chezou/tabula-py) documentation
> `tabula-py` is a simple Python wrapper of [tabula-java](https://github.com/tabulapdf/tabula-java), which can read table of PDF.
> You can read tables from PDF and convert into `pandas` DataFrame.
* If you don't have it already, install [Java](https://www.java.com/en/download/manual.jsp)
* Try to run `python webscraper_main.py`.
* If there's a `FileNotFoundError` when it calls `read_pdf()`, and when you type `java` on command line it says
`'java' is not recognized as an internal or external command, operable program or batch file`, you should set `PATH` environment variable to point to the Java directory.
* Find the main Java folder like `jre...` or `jdk...`. On Windows 10 it was under `C:\Program Files\Java`
* On Windows 10: **Control Panel** -> **System and Security** -> **System** -> **Advanced System Settings** -> **Environment Variables** -> Select **PATH** --> **Edit**
* Add the `bin` folder like `C:\Program Files\Java\jre1.8.0_144\bin`, hit OK a bunch of times.
* On command line, `java` should now print a list of options, and `tabula.read_pdf()` should run.

## PDF-to-dataframe conversion
* To get the right columns in dataframe I had to find X/Y coordinates manually. Coords specified as arguments to `tabula.read_pdf()`: bounding box containing the table and X coords of column boundaries.
* If their PDF ever changes, you can re-find the coordinates by running `tabula.exe` in [tabula](tabula) folder (also downloadable [here](http://tabula.technology/)). [Tabula-Java wiki](https://github.com/tabulapdf/tabula-java/wiki/Using-the-command-line-tabula-extractor-tool#grab-coordinates-of-the-table-you-want) explains how to do this.
> Select your table area(s) as usual and proceed to the "Preview & Export Extracted Data" step.
> Under Export Format, select "Script" instead of CSV, and then click "Export" to download the generated code.

## Results
[As per the specifications](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md#csv-columns-in-order), the resulting CSV includes the following columns:

| Column Name       | Data Available
|-------------------|---------------|
| county_name       | ✓ |
| timestamp         | ✓ |
| url               | ✓ |
| inmate_id         | ✗ |
| inmate_lastname   | ✓ |
| inmate_firstname  | ✓ |
| inmate_middlename | ✓ |
| inmate_sex        | ✓ |
| inmate_race       | ✓ |
| inmate_age        | ✓ |
| inmate_dob        | ✗ |
| inmate_address    | ✗ |
| booking_timestamp | Day only |
| release_timestamp | ✗ |
| processing_numbers| ✗ |
| agency            | ✗ |
| facility          | ✓ |
| charges           | ✓ |
| severity          | For some charges |
| bond_amount       | ✗ |
| current_status    | For some charges |
| court_dates       | ✗ |
| days_jailed       | ✓ |
| other             | ✗ |
| notes				| ✓ |
