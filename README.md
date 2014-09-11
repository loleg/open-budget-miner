This script is used to read in the budget data of the Canton of Bern from PDF.

Requires Python 2+ and pdfminer

## Data sources

- [Canton of Bern Budget 2013-2014](http://www.be.ch/portal/de/index/mediencenter/medienmitteilungen.assetref/dam/documents/portal/Medienmitteilungen/de/2013/06/2013-06-28-asp-2014-bericht-de.pdf) (PDF)

## Usage instructions

Use `virtualbox` to create a local env, then
```
$ pip install -r requirements.txt
```
Run the script appending the PDF filename
```
$ python mine.py data/sample.pdf > output/sample.json
```

## Alternative usage with pdfminer

Download and compile pdfminer
```
$ git clone https://github.com/euske/pdfminer.git
```
Make a symlink in this folder
```
$ ln -s ../pdfminer/build/lib/pdfminer
```
Run the script appending the PDF filename
```
$ python mine.py data/sample.pdf > output/sample.json
```
