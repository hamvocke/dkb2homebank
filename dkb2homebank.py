#! /usr/bin/env python

import argparse
import csv
from datetime import datetime


class DKB(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL


csv.register_dialect("dkb", DKB)

dkb_field_names = ["buchungstag",
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


visa_field_names = ["abgerechnet",
                    "wertstellung",
                    "belegdatum",
                    "umsatzbeschreibung",
                    "betrag",
                    "urspruenglicherBetrag"]

homebank_field_names = ["date",
                        "paymode",
                        "info",
                        "payee",
                        "memo",
                        "amount",
                        "category",
                        "tags"]


def convert_DKB_cash(filename):
    with open(filename, 'r', encoding='iso-8859-1') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(transaction_lines(csvfile), dialect=dialect, fieldnames=dkb_field_names)

        with open("cashHomebank.csv", 'w') as outfile:
            writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebank_field_names)
            for row in reader:
                writer.writerow(
                    {
                        'date': convert_date(row["buchungstag"]),
                        'paymode': 8,
                        'info': None,
                        'payee': row["beguenstigter"],
                        'memo': row["verwendungszweck"],
                        'amount': row["betrag"],
                        'category': None,
                        'tags': None
                    })


def convert_visa(filename):
    with open(filename, 'r', encoding='iso-8859-1') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(transaction_lines(csvfile), dialect=dialect, fieldnames=visa_field_names)

        with open("visaHomebank.csv", 'w') as outfile:
            writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebank_field_names)
            for row in reader:
                writer.writerow(
                    {
                        'date': convert_date(row["wertstellung"]),
                        'paymode': 1,
                        'info': None,
                        'payee': None,
                        'memo': row["umsatzbeschreibung"],
                        'amount': row["betrag"],
                        'category': None,
                        'tags': None
                    })


def transaction_lines(file):
    """
    Reduce the csv lines to the lines containing actual data relevant for the conversion.

    :param file: The export CSV from DKB to be converted
    :return: The lines containing the actual transaction data
    """
    lines = file.readlines()
    i = 1
    for line in lines:
        if "Betrag" in line:
            return lines[i:]
        i = i + 1

    raise ValueError("Can't convert CSV file without header line")


def convert_date(date_string):
    date = datetime.strptime(date_string, "%d.%m.%Y")
    return date.strftime('%d-%m-%Y')


def main():
    parser = argparse.ArgumentParser(description=
                                     "Convert a CSV export file from DKB online banking "
                                     "to a Homebank compatible CSV format.")
    parser.add_argument("filename", help="The CSV file to convert.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--visa", action="store_true", help="convert a DKB Visa account CSV file")
    group.add_argument("-c", "--cash", action="store_true", help="convert a DKB Cash account CSV file")

    args = parser.parse_args()

    if args.visa:
        convert_visa(args.filename)
        print("DKB Visa file converted. Output file: 'visaHomebank.csv'")
    elif args.cash:
        convert_DKB_cash(args.filename)
        print("DKB Cash file converted. Output file: 'cashHomebank.csv'")
    else:
        print("You must provide the type of the CSV file (--cash for DKB Cash, --visa for DKB Visa)")


if __name__ == '__main__':
    main()
