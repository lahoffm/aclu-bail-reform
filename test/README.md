# CSV Data Validator

Tests that all CSV files in `data` is in format described by [CONTRIBUTING.md](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md).

## Installation Requirements
- Python 3.6.3
- colorama 0.3.9

```
pip install -r requirements.txt
```

## To Run

```
python csv_validator.py
```

- Validates all files ending in *.csv* in `data` folder
- Outputs results to terminal and a log file in `logs` folder
- Overwrites same day log file
- For validation specifications, read comments in `validator.py`
- Even if tests pass, many other things can go wrong, so eyeball check of CSV files is strongly recommended.

**Warning:** An error in one field of a row most likely means the same error exists in all rows for that field. In such cases, log may be repetitive.