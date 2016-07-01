#! /usr/bin/env python

import argparse
import csv
from datetime import datetime

class dkb(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL

csv.register_dialect("dkb", dkb)

dkbFieldNames = ["buchungstag",
                  "wertstellung",
                  "buchungstext",
                  "beguenstigter",
                  "verwendungszweck",
                  "kontonummer",
                  "blz",
                  "betrag",
                  "glaeubigerID",
                  "mandatsreferenz",
                  "kundenreferenz"]


visaFieldNames =    ["abgerechnet",
                     "wertstellung",
                     "belegdatum",
                     "umsatzbeschreibung",
                     "betrag",
                     "urspruenglicherBetrag"]

homebankFieldNames = ["date",
                      "paymode",
                      "info",
                      "payee",
                      "memo",
                      "amount",
                      "category",
                      "tags"]


def convertDkbCash(filename):
    with open(filename, 'r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(transactionLines(csvfile), dialect=dialect, fieldnames=dkbFieldNames)

        with open("cashHomebank.csv", 'w') as outfile:
            writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebankFieldNames)
            for row in reader:
                writer.writerow(
                    {
                    'date': convertDate(row["buchungstag"]),
                    'paymode': 8,
                    'info': None,
                    'payee': row["beguenstigter"],
                    'memo': row["verwendungszweck"],
                    'amount': row["betrag"],
                    'category': None,
                    'tags': None
                    })

def convertVisa(filename):
    with open(filename, 'r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(transactionLines(csvfile), dialect=dialect, fieldnames=visaFieldNames)

        with open("visaHomebank.csv", 'w') as outfile:
            writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebankFieldNames)
            for row in reader:
                writer.writerow(
                    {
                    'date': convertDate(row["wertstellung"]),
                    'paymode': 1,
                    'info': None,
                    'payee': None,
                    'memo': row["umsatzbeschreibung"],
                    'amount': row["betrag"],
                    'category': None,
                    'tags': None
                    })

def transactionLines(file):
    lines = file.readlines()
    i = 1
    for line in lines:
        if "Betrag" in line:
            return lines[i:]
        i = i + 1

def convertDate(dateString):
    date = datetime.strptime(dateString, "%d.%m.%Y")
    return date.strftime('%d-%m-%Y')

def main():
    parser = argparse.ArgumentParser(description="Convert a CSV export file from DKB online banking to a Homebank compatible CSV format.")
    parser.add_argument("filename", help="The CSV file to convert.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--visa", action="store_true", help="convert a DKB Visa account CSV file")
    group.add_argument("-c", "--cash", action="store_true", help="convert a DKB Cash account CSV file")

    args = parser.parse_args()

    if args.visa:
        convertVisa(args.filename)
        print("DKB Visa file converted. Output file: 'visaHomebank.csv'")
    elif args.cash:
        convertDkbCash(args.filename)
        print("DKB Cash file converted. Output file: 'cashHomebank.csv'")
    else:
        print("You must provide the type of the CSV file (--cash for DKB Cash, --visa for DKB Visa)")


if __name__ == '__main__':
    main()
