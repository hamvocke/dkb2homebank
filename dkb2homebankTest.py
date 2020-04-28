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
        dkb2homebank.convert_DKB_cash('testfiles/cash.csv', 'cashHomebank.csv')
        lineNumber = sum(1 for line in open('cashHomebank.csv'))
        self.assertEqual(lineNumber, 2)

    def testShouldConvertCashFileAndWriteToAlternativeOutputDir(self):
        tmpdir = tempfile.gettempdir()
        dkb2homebank.convert_DKB_cash('testfiles/cash.csv', os.path.join(tmpdir, "cashHomebank.csv"))

    def testThrowErrorForEmptyCashFile(self):
        with self.assertRaises(ValueError) as context:
            dkb2homebank.convert_DKB_cash('testfiles/cash_empty.csv')

        self.assertTrue("Can't convert CSV file without header line" in str(context.exception))

    def testShouldConvertVisaFile(self):
        dkb2homebank.convert_visa('testfiles/visa.csv', 'visaHomebank.csv')
        lineNumber = sum(1 for line in open('visaHomebank.csv'))
        self.assertEqual(lineNumber, 4)

    def testShouldConvertVisaFileWithRange(self):
        dkb2homebank.convert_visa('testfiles/visaRange.csv', 'visaHomebank.csv')
        lineNumber = sum(1 for line in open('visaHomebank.csv'))
        self.assertEqual(lineNumber, 1)

    def tearDown(self):
        self.delete('cashHomebank.csv')
        self.delete('visaHomebank.csv')

    def delete(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)


class DKB2HomebankFunctionalTest(unittest.TestCase):
    def testShouldRunScriptWithCashParameter(self):
        result = subprocess.run(["./dkb2homebank.py", "--cash", "testfiles/cash.csv"])
        self.assertEqual(0, result.returncode)

    def testShouldRunScriptWithVisaParameter(self):
        result = subprocess.run(["./dkb2homebank.py", "--visa", "testfiles/visa.csv"])
        self.assertEqual(0, result.returncode)

    def testShouldRunScriptWithOutputParameter(self):
        result = subprocess.run(["./dkb2homebank.py", "--cash", "testfiles/cash.csv", "--output-file", "/tmp/dkb2homebank.csv"])
        self.assertEqual(0, result.returncode)


if __name__ == '__main__':
    unittest.main()
