# Cobb County Jail Webscraper

This code was written in Python 3.6, and relies on packages `requests`, `re`, `sys`, `csv`, `pandas`, `numpy`, `bs4`, `datetime`, and `math`. All of these packages can installed via the `pip install` method.
The code automatically uses the current date it is being run and submits the url to receive the last three days of arrest records from Cobb County's website.
Following line of `cobb_scraper.py` will need adjustment to the location you wish to have the file stored at:

```python
with open(r'../../../data/cobb_'+stamp+'-'+full_time+'.csv', 'w') as csvfile:
```

To run: `python cobb_scraper.py`