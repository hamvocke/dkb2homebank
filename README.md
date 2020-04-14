dkb2homebank
============

This script converts CSV account reports from [Deutsche Kreditbank (DKB)](https://www.dkb.de) to a
CSV format that can be imported by the personal finance software
[Homebank](http://homebank.free.fr/).

You can find further instructions on [my blog](http://www.hamvocke.com/blog/import-dkb-accounts-into-homebank/).

How to run the script
---------------------
The script can either convert a _DKB Cash_ account report or a _Visa_ account report CSV file.

To convert a _DKB Cash_ CSV file simply run:
    
    ./dkb2homebank.py --cash yourCashReportFile.csv

To convert a _Visa_ CSV file run:
    
    ./dkb2homebank.py --visa yourVisaReportFile.csv
    
You can also choose an alternative path for your output file, if the standard "cashHomebank.csv" or "visaHomebank.csv" in the working directory doesn't do it for you. Use `--output-dir` or `-o` for that:
 
    ./dkb2homebank.py --cash yourCashReportFile.csv --output-dir ~/Documents/Finances/import_to_homebank.csv


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
