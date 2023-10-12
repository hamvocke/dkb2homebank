#! /usr/bin/env python3

import argparse
import csv
from datetime import datetime


class DKB(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL


class InvalidInputException(Exception):
    """Exception for input CSVs that seem not to be valid DKB input files."""
    def __init__(self, message):
        self.message = message


csv.register_dialect("dkb", DKB)

cash_field_names = ["buchungstag",
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

giro_field_names = ["buchungsdatum",
                   "wertstellung",
                   "status",
                   "zahlungspflichtige*r",
                   "zahlungsempfänger*in",
                   "verwendungszweck",
                   "umsatztyp",
                   "betrag",
                   "gläubiger-id",
                   "mandatsreferenz",
                   "kundenreferenz"]

homebank_field_names = ["date",
                        "paymode",
                        "info",
                        "payee",
                        "memo",
                        "amount",
                        "category",
                        "tags"]

def _open_csv(file_path, field_names, encoding):
    with open(file_path, 'r', encoding=encoding) as file:
        dialect = csv.Sniffer().sniff(file.read(1024))
        file.seek(0)
        return csv.DictReader(find_transaction_lines(file), dialect=dialect, fieldnames=field_names)

def convert_cash(file_path, output_file="cashHomebank.csv"):
    """
    Convert a DKB cash file (i.e. normal bank account) to a homebank-readable import CSV.

    :param file_path: file path of the file to be converted
    :param output_file: the output file path as a string
    """
    reader = _open_csv(file_path, cash_field_names, 'iso-8859-1')
    with open(output_file, 'w', encoding='utf-8') as outfile:
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


def convert_visa(file_path, output_file="visaHomebank.csv"):
    """
    Convert a DKB visa file to a homebank-readable import CSV.

    :param file_path: file path of the file to be converted
    :param output_file: the output file path as a string
    """
    reader = _open_csv(file_path, visa_field_names, 'iso-8859-1')
    with open(output_file, 'w', encoding='utf-8') as outfile:
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

def convert_giro(file_path, output_file="giroHomebank.csv"):
    """
    Convert a DKB giro file (i.e. the normal bank account file available in the
    new banking portal introduced in 2023) to a homebank-readable import CSV.

    :param file_path: file path of the file to be converted
    :param output_file: the output file path as a string
    """
    reader = _open_csv(file_path, giro_field_names, 'utf-8-sig')
    with open(output_file, 'w', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebank_field_names)
        for row in reader:
            writer.writerow(
                {
                    'date': convert_short_date(row["buchungsdatum"]),
                    'paymode': 8,
                    'info': None,
                    'payee': row["zahlungsempfänger*in"],
                    'memo': row["verwendungszweck"],
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
        # appear in headers of the cash, visa, and giro CSVs.
        if "Betrag" in line and "Wertstellung" in line:
            return lines[i:]
        i = i + 1

    raise ValueError("Can't convert CSV file without header line")


def convert_date(date_string):
    """Convert the date_string to dd-mm-YYYY format."""
    date = datetime.strptime(date_string, "%d.%m.%Y")
    return date.strftime('%d-%m-%Y')

def convert_short_date(date_string):
    """Convert the date_string to dd-mm-YYYY format."""
    date = datetime.strptime(date_string, "%d.%m.%y")
    return date.strftime('%d-%m-%Y')

def setup_parser():
    parser = argparse.ArgumentParser(description=
                                     "Convert a CSV export file from DKB online banking "
                                     "to a Homebank compatible CSV format.")
    parser.add_argument("filename", help="The CSV file to convert.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-v", "--visa", action="store_true", help="convert a DKB Visa account CSV file")
    group.add_argument("-c", "--cash", action="store_true", help="convert a DKB Cash account CSV file")
    group.add_argument("-g", "--giro", action="store_true", help="convert a DKB Giro account CSV file (newly introduced in 2023)")

    parser.add_argument('-o', '--output-file', help='choose where to store the output file (default: working directory')

    parser.add_argument('--debug', '-d', help='output some information to STDERR')

    return parser.parse_args()


def main():

    args = setup_parser()

    if args.visa:
        output = args.output_file or "visaHomebank.csv"
        convert_visa(args.filename, output)
        print(f"DKB Visa file converted. Output file: {output}") if args.debug else None
    elif args.cash:
        output = args.output_file or "cashHomebank.csv"
        convert_cash(args.filename, output)
        print(f"DKB Cash file converted. Output file: {output}") if args.debug else None
    elif args.giro:
        output = args.output_file or "giroHomebank.csv"
        convert_giro(args.filename, output)
        print(f"DKB Giro file converted. Output file: {output}") if args.debug else None


if __name__ == '__main__':
    main()
