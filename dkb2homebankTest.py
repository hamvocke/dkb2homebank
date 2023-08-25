#! /usr/bin/env python3

from builtins import ResourceWarning
import unittest
import dkb2homebank
import os
import warnings
import tempfile
import subprocess


class DKB2HomebankTest(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def testShouldConvertCashFile(self):
        with open(r'testfiles/cash.csv', encoding='iso-8859-1') as csv_file:
            dkb2homebank.convert_cash(csv_file, 'cashHomebank.csv')
            csv_file.seek(0)
            lineNumber = len(dkb2homebank.find_transaction_lines(csv_file))
            self.assertEqual(lineNumber, 2)

    def testShouldConvertCashFileAndWriteToAlternativeOutputDir(self):
        with open(r'testfiles/cash.csv', encoding='iso-8859-1') as csv_file:
            tmpdir = tempfile.gettempdir()
            dkb2homebank.convert_cash(csv_file, os.path.join(tmpdir, "cashHomebank.csv"))

    def testThrowErrorForEmptyCashFile(self):
        with self.assertRaises(ValueError) as context:
            with open('testfiles/cash_empty.csv', encoding='iso-8859-1') as csv_file:
                dkb2homebank.convert_cash(csv_file)
        self.assertTrue("Can't convert CSV file without header line" in str(context.exception))

    def testShouldConvertVisaFile(self):
        with open('testfiles/visa.csv', encoding='iso-8859-1') as csv_file:
            dkb2homebank.convert_visa(csv_file, 'visaHomebank.csv')
            csv_file.seek(0)
            lineNumber = len(dkb2homebank.find_transaction_lines(csv_file))
        self.assertEqual(lineNumber, 4)

    def testShouldConvertVisaFileWithRange(self):
        with open('testfiles/visaRange.csv', encoding='iso-8859-1') as csv_file:
            dkb2homebank.convert_visa(csv_file, 'visaHomebank.csv')
            csv_file.seek(0)
            lineNumber = len(dkb2homebank.find_transaction_lines(csv_file))
            self.assertEqual(lineNumber, 1)

    def testShouldConvertGiroFile(self):
        with open('testfiles/giro.csv', encoding='iso-8859-1') as csv_file:
            dkb2homebank.convert_giro(csv_file, 'giroHomebank.csv')
            csv_file.seek(0)
            lineNumber = len(dkb2homebank.find_transaction_lines(csv_file))
        self.assertEqual(lineNumber, 5)

    def tearDown(self):
        self.delete('cashHomebank.csv')
        self.delete('visaHomebank.csv')
        self.delete('giroHomebank.csv')

    def delete(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)


class DKB2HomebankFunctionalTest(unittest.TestCase):
    def testShouldRunScriptWithCashFlag(self):
        result = subprocess.run(["./dkb2homebank.py", "--cash", "testfiles/cash.csv"])
        self.assertEqual(0, result.returncode)

    def testShouldRunScriptWithVisaFlag(self):
        result = subprocess.run(["./dkb2homebank.py", "--visa", "testfiles/visa.csv"])
        self.assertEqual(0, result.returncode)

    def testShouldRunScriptWithGiroFlag(self):
        result = subprocess.run(["./dkb2homebank.py", "--giro", "testfiles/giro.csv"])
        self.assertEqual(0, result.returncode)

    def testShouldRunScriptWithOutputParameter(self):
        result = subprocess.run(["./dkb2homebank.py", "--cash", "testfiles/cash.csv", "--output-file", "/tmp/dkb2homebank.csv"])
        self.assertEqual(0, result.returncode)


if __name__ == '__main__':
    unittest.main()
