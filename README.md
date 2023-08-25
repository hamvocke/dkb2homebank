dkb2homebank ![Python application](https://github.com/hamvocke/dkb2homebank/workflows/Python%20application/badge.svg)
============

This script converts CSV account reports from [Deutsche Kreditbank (DKB)](https://www.dkb.de) to a
CSV format that can be imported by the personal finance software
[Homebank](http://homebank.free.fr/).

You can find further instructions on [my blog](http://www.hamvocke.com/blog/import-dkb-accounts-into-homebank/).

How to run the script
---------------------

The script can detect what kind of account's CSV export you want to convert. Currently supported are:

* DKB Cash (as of the legacy web portal)
* DKB Visa (as of the legacy web portal)
* DKB Giro (as of the new web portal introduced in 2023)

Simply run the following command to let the script auto-detect the kind of CSV file you're passing in:

	./dkb2homebank.py yourDKBExportFile.csv

If auto-detection doesn't work or you prefer to be explicit, you can pass the account type with the `-v|-c|-g` switch:

To convert a _DKB Cash_ file run:
    
    ./dkb2homebank.py --cash yourCashReportFile.csv

To convert a _Visa_ file run:
    
    ./dkb2homebank.py --visa yourVisaReportFile.csv
    
To convert a _Giro_ file (that's the new format introduced with the 2023 web portal overhaul) run:
    
    ./dkb2homebank.py --visa yourGiroReportFile.csv
    
You can also choose an alternative path for your output file, if the standard "Homebank.csv" in the working directory doesn't do it for you. Use `--output-file` or `-o` for that:
 
    ./dkb2homebank.py --cash yourCashReportFile.csv --output-file ~/Documents/Finances/import_to_homebank.csv


Importing into Homebank
-----------------------
Import the converted CSV file into Homebank by going to `File -> Import` and selecting the _output_ file you got when running your script.

**Note**: If Homebank tells you that your CSV file is invalid, go to `Settings -> Import/Export` and make sure that the `Delimiter` is set to `semicolon` and try importing again.

Requirements
------------
To run this script, you need Python 3.4 or higher. I've verified that the exported CSV can be imported successfully on Homebank *5.0.0* and above.

Run the tests
-------------
I have included a (admittedly very small) set of tests to help a little bit during development.
These tests use Python's _unittest_ module and can be executed using:
    
    ./dkb2homebankTest.py

You can also test the script manually by using the provided testfiles:

    ./dkb2homebank.py --cash testfiles/cash.csv
   
or

    ./dkb2homebank.py --visa testfiles/visa.csv
    
or

    ./dkb2homebank.py --giro testfiles/giro.csv
