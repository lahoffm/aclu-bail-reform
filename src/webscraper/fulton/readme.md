# Fulton County Jail Webscraper

This code was written in **Python 3.6**, and relies on **selenium** and **BeautifulSoup4**.
Both of these packages can installed via `pip install requirements.txt`.

If you are using Chrome on Windows, the selenium driver `chromedriver.exe` has already been placed in this directory.
It runs **ChromeDriver 2.33**, which supports Chrome v60-62 according to selenium docs.

Otherwise, selenium will require that a driver be placed in this directory. See [link](http://selenium-python.readthedocs.io/installation.html) for details.

Following lines of `reg_script.py` will need adjustment if using a setup other than Chrome on Windows.
```python
chrome_path = os.path.join(dir_path,"chromedriver")
driver = webdriver.Chrome(chrome_path)
```
