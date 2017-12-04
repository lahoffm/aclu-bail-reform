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
- Outputs results to terminal and a log file in `logs` folder.
- Even if tests pass, many other things can go wrong, so eyeball check of CSV files is strongly recommended.