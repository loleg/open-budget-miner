This script is used to read in the budget data of the Canton of Bern from PDF.

Requires Python 2 and pdfminer

# Usage:

1. download and compile pdfminer
```
$ git clone https://github.com/euske/pdfminer.git
```
2. make a symlink in this folder
```
$ ln -s ../pdfminer/build/lib/pdfminer
```
3. run the script appending the PDF filename
```
$ python mine.py data/sample.pdf > output/sample.json
```

# Data sources:

- [Canton of Bern Budget 2013-2014](http://www.be.ch/portal/de/index/mediencenter/medienmitteilungen.assetref/dam/documents/portal/Medienmitteilungen/de/2013/06/2013-06-28-asp-2014-bericht-de.pdf) (PDF)
