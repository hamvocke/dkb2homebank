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


def convert_DKB_cash(filename, output_file="cashHomebank.csv"):
    """
    Write a CSV with output consumable by Homebank's import functionality.

    :param filename: the input file path as a string
    :param output_file: the output file path as a string
    """
    with open(filename, 'r', encoding='iso-8859-1') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(find_transaction_lines(csvfile), dialect=dialect, fieldnames=dkb_field_names)

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


def convert_visa(filename, output_file="visaHomebank.csv"):
    """
    Convert a DKB visa file to a homebank-readable import CSV.

    :param filename: Path to the file to be converted
    """
    with open(filename, 'r', encoding='iso-8859-1') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(find_transaction_lines(csvfile), dialect=dialect, fieldnames=visa_field_names)

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


def find_transaction_lines(file):
    """
    Reduce the csv lines to the lines containing actual data relevant for the conversion.

    :param file: The export CSV from DKB to be converted
    :return: The lines containing the actual transaction data
    """
    lines = file.readlines()
    i = 1
    for line in lines:
        # simple heuristic to find the csv header line. Both these strings
        # appear in headers of the cash and visa CSVs.
        if "Betrag" in line and "Wertstellung" in line:
            return lines[i:]
        i = i + 1

    raise ValueError("Can't convert CSV file without header line")


def convert_date(date_string):
    """Convert the date_string to dd-mm-YYYY format."""
    date = datetime.strptime(date_string, "%d.%m.%Y")
    return date.strftime('%d-%m-%Y')


def setup_parser():
    parser = argparse.ArgumentParser(description=
                                     "Convert a CSV export file from DKB online banking "
                                     "to a Homebank compatible CSV format.")
    parser.add_argument("filename", help="The CSV file to convert.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--visa", action="store_true", help="convert a DKB Visa account CSV file")
    group.add_argument("-c", "--cash", action="store_true", help="convert a DKB Cash account CSV file")

    parser.add_argument('-o', '--output-dir', help='choose where to store the output file (default: working directory')

    return parser.parse_args()


def main():

    args = setup_parser()

    if args.visa:
        convert_visa(args.filename, args.output_file)
        print("DKB Visa file converted. Output file: %s" % args.output_file)
    elif args.cash:
        convert_DKB_cash(args.filename, args.output_file)
        print("DKB Cash file converted. Output file: %s" % args.output_file)
    else:
        print("You must provide the type of the CSV file (--cash for DKB Cash, --visa for DKB Visa)")


if __name__ == '__main__':
    main()
