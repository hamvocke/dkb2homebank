#! /usr/bin/env python3

from builtins import ResourceWarning
import unittest
import dkb2homebank
import os
import warnings
import subprocess
import filecmp

def fileContentEqual(file1, file2):
    return filecmp.cmp(file1, file2)

class DKB2HomebankTest(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def testShouldConvertCashFile(self):
        dkb2homebank.convert_cash('testfiles/cash.csv', 'cashHomebank.csv')
        self.assertTrue(fileContentEqual('testfiles/expected-output/cashHomebank.csv', 'cashHomebank.csv'))

    def testThrowErrorForEmptyCashFile(self):
        with self.assertRaises(ValueError) as context:
            dkb2homebank.convert_cash('testfiles/cash_empty.csv')
        self.assertTrue("Can't convert CSV file without header line" in str(context.exception))

    def testShouldConvertVisaFile(self):
        dkb2homebank.convert_old_visa('testfiles/visa.csv', 'visaHomebank.csv')
        self.assertTrue(fileContentEqual('testfiles/expected-output/visaHomebank.csv', 'visaHomebank.csv'))

    def testShouldConvertVisaFileWithRange(self):
        dkb2homebank.convert_old_visa('testfiles/visaRange.csv', 'visaHomebank.csv')
        self.assertTrue(fileContentEqual('testfiles/expected-output/visaRangeHomebank.csv', 'visaHomebank.csv'))

    def testShouldConvertGiroFile(self):
        dkb2homebank.convert_giro('testfiles/giro.csv', 'giroHomebank.csv')
        self.assertTrue(fileContentEqual('testfiles/expected-output/giroHomebank.csv', 'giroHomebank.csv'))

    def testShouldDetectOldCashFile(self):
        format = dkb2homebank.detect_csv_format('testfiles/cash.csv')
        self.assertEqual(format, dkb2homebank.CsvFileTypes.CASH)

    def testShouldDetectOldVisaFile(self):
        format = dkb2homebank.detect_csv_format('testfiles/visa.csv')
        self.assertEqual(format, dkb2homebank.CsvFileTypes.OLD_VISA)

    def testShouldDetectNewGiroFile(self):
        format = dkb2homebank.detect_csv_format('testfiles/giro.csv')
        self.assertEqual(format, dkb2homebank.CsvFileTypes.GIRO)

    def testShouldDetectNewVisaFile(self):
        format = dkb2homebank.detect_csv_format('testfiles/visaNew.csv')
        self.assertEqual(format, dkb2homebank.CsvFileTypes.NEW_VISA)

    def tearDown(self):
        delete('cashHomebank.csv')
        delete('visaHomebank.csv')
        delete('giroHomebank.csv')


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

    def testShouldRunScriptWithoutExplicitFileTypeFlag(self):
        result = subprocess.run(["./dkb2homebank.py", "testfiles/cash.csv"])
        self.assertEqual(0, result.returncode)
    
    def tearDown(self):
        delete('cashHomebank.csv')
        delete('visaHomebank.csv')
        delete('giroHomebank.csv')

def delete(filename):
    if os.path.isfile(filename):
        os.remove(filename)

if __name__ == '__main__':
    unittest.main()
