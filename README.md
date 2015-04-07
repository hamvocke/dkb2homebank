dkb2homebank
============

This script converts CSV account reports from [Deutsche Kreditbank (DKB)](https://www.dkb.de) to a
CSV format that can be imported by the personal finance software
[Homebank](http://homebank.free.fr/).

How to run the script
---------------------
The script can either convert a _DKB Cash_ account report or a _Visa_ account report CSV file.

To convert a _DKB Cash_ CSV file simply run:
    
    dkb2homebank.py --cash yourCashReportFile.csv

To convert a _Visa_ CSV file run:
    
    dkb2homebank.py --visa yourVisaReportFile.csv


Tested versions
---------------
I have tested the script with Python versions *2.7.9* and *3.4.3* and Homebank *5.0.0* on Arch Linux. I expect it to run with similar versions on other operating systems as well.

Run the tests
-------------
I have included a (admittedly very small) set of tests to help a little bit during development.
These tests use Python's _unittest_ module and can be executed using:
    
    python dkb2homebankTest.py


